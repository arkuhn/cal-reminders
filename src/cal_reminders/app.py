import subprocess
import webbrowser
import rumps
from datetime import datetime, timezone

from .calendar import CalendarService, Event, extract_meeting_link
from .config import load_config


def is_login_item() -> bool:
    """Check if app is registered as a login item."""
    result = subprocess.run(
        ["osascript", "-e", 
         'tell application "System Events" to get the name of every login item'],
        capture_output=True, text=True
    )
    return "Cal Reminders" in result.stdout


def set_login_item(enabled: bool) -> None:
    """Add or remove app from login items."""
    app_path = "/Applications/Cal Reminders.app"
    if enabled:
        subprocess.run([
            "osascript", "-e",
            f'tell application "System Events" to make login item at end with properties {{path:"{app_path}", hidden:false}}'
        ])
    else:
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to delete login item "Cal Reminders"'
        ])


def truncate(text: str, max_len: int = 20) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def format_countdown(event: Event) -> str:
    """Format the countdown string for the menubar.
    
    > 1 hour:  "2h 15m"
    > 5 min:   "45m"
    ≤ 5 min:   "4:59" (with seconds)
    ≤ 10 sec:  Pulsing red/white icon
    """
    now = datetime.now(timezone.utc)
    delta = event.start_time - now
    total_seconds = int(delta.total_seconds())

    if total_seconds <= 0:
        return f"🔴 NOW — {truncate(event.title)}"

    total_minutes = total_seconds // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    seconds = total_seconds % 60

    # Pulsing icon when ≤ 10 seconds
    if total_seconds <= 10:
        icon = "🔴" if seconds % 2 == 0 else "⚪"
    else:
        icon = "⏱"

    if hours > 0:
        if minutes > 0:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{hours}h"
    elif total_minutes > 5:
        time_str = f"{total_minutes}m"
    else:
        time_str = f"{minutes}:{seconds:02d}"

    return f"{icon} {time_str} — {truncate(event.title)}"


def format_relative_time(event: Event) -> str:
    """Format relative time like 'in 4 min' or 'in 1h 30m'."""
    now = datetime.now(timezone.utc)
    delta = event.start_time - now
    total_minutes = int(delta.total_seconds() / 60)

    if total_minutes < 1:
        return "now"
    elif total_minutes < 60:
        return f"in {total_minutes} min"
    else:
        hours = total_minutes // 60
        mins = total_minutes % 60
        if mins == 0:
            return f"in {hours}h"
        return f"in {hours}h {mins}m"


class CalRemindersApp(rumps.App):
    def __init__(self):
        super().__init__("⏱ Loading...")
        self.config = load_config()
        self.calendar_service = None
        self.next_event: Event | None = None
        self.upcoming_events: list[Event] = []
        self.meeting_link: tuple[str, str] | None = None

        self.menu = [
            rumps.MenuItem("Loading...", callback=None),
            None,
            rumps.MenuItem("Refresh Now", callback=self.refresh_events),
            None,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

        self.calendar_service = CalendarService()
        
        if not self.calendar_service.wait_for_access(timeout=30):
            self.title = "⚠️ No calendar access"
            self.menu = [
                rumps.MenuItem("Calendar access required", callback=None),
                rumps.MenuItem("Open Privacy Settings...", callback=self.open_privacy_settings),
                None,
                rumps.MenuItem("Quit", callback=rumps.quit_application),
            ]
            return

        self.refresh_events(None)

        self.display_timer = rumps.Timer(self.update_display, 1)
        self.display_timer.start()

        refresh_interval = self.config["refresh_interval_seconds"]
        self.refresh_timer = rumps.Timer(self.refresh_events, refresh_interval)
        self.refresh_timer.start()

    def refresh_events(self, _):
        """Fetch latest events from calendar."""
        if not self.calendar_service:
            return

        try:
            self.upcoming_events = self.calendar_service.get_upcoming_events(count=3)
            self.next_event = self.upcoming_events[0] if self.upcoming_events else None
            self.meeting_link = None
            if self.next_event:
                self.meeting_link = extract_meeting_link(self.next_event)
            self.update_menu()
        except Exception as e:
            print(f"Error fetching events: {e}")

    def join_meeting(self, _):
        """Open the meeting link in the default browser."""
        if self.meeting_link:
            webbrowser.open(self.meeting_link[0])

    def open_privacy_settings(self, _):
        """Open System Settings to Privacy & Security > Calendars."""
        subprocess.run([
            "open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Calendars"
        ])

    def toggle_login_item(self, sender):
        """Toggle Launch at Login setting."""
        new_state = not sender.state
        set_login_item(new_state)
        sender.state = new_state

    def open_in_calendar(self, _):
        """Open Calendar.app."""
        subprocess.run(["open", "-a", "Calendar"])

    def update_menu(self):
        """Update the dropdown menu content."""
        self.menu.clear()

        login_item = rumps.MenuItem("Launch at Login", callback=self.toggle_login_item)
        login_item.state = is_login_item()

        if self.next_event:
            relative = format_relative_time(self.next_event)
            start_str = self.next_event.start_time.astimezone().strftime("%-I:%M")
            end_str = self.next_event.end_time.astimezone().strftime("%-I:%M %p")

            menu_items = [
                rumps.MenuItem(f"📅 {self.next_event.title}", callback=None),
                rumps.MenuItem(f"   {relative} · {start_str} - {end_str}", callback=None),
            ]

            if self.meeting_link:
                url, meeting_type = self.meeting_link
                menu_items.append(rumps.MenuItem(f"🔗 Join {meeting_type}", callback=self.join_meeting))

            # Show next 2 events if available
            if len(self.upcoming_events) > 1:
                menu_items.append(None)  # Separator
                menu_items.append(rumps.MenuItem("Next up:", callback=None))
                for event in self.upcoming_events[1:3]:
                    time_str = event.start_time.astimezone().strftime("%-I:%M %p")
                    menu_items.append(
                        rumps.MenuItem(f"   📅 {truncate(event.title, 25)} ({time_str})", callback=None)
                    )

            menu_items.extend([
                None,
                rumps.MenuItem("Open Calendar", callback=self.open_in_calendar),
                rumps.MenuItem("Refresh Now", callback=self.refresh_events),
                login_item,
                None,
                rumps.MenuItem("Quit", callback=rumps.quit_application),
            ])

            self.menu = menu_items
        else:
            self.menu = [
                rumps.MenuItem("No upcoming events", callback=None),
                None,
                rumps.MenuItem("Open Calendar", callback=self.open_in_calendar),
                rumps.MenuItem("Refresh Now", callback=self.refresh_events),
                login_item,
                None,
                rumps.MenuItem("Quit", callback=rumps.quit_application),
            ]

    def update_display(self, _):
        """Update the menubar title with current countdown."""
        if not self.next_event:
            self.title = "⏱ No events"
            return

        now = datetime.now(timezone.utc)

        if self.next_event.start_time <= now:
            self.refresh_events(None)
            return

        self.title = format_countdown(self.next_event)


def main():
    app = CalRemindersApp()
    app.run()


if __name__ == "__main__":
    main()
