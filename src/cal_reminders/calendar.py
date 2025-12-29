from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import re
import threading

from EventKit import EKEventStore, EKEntityTypeEvent
from Foundation import NSDate

from .config import load_config


MEETING_PATTERNS = [
    (r'https://[\w.-]*zoom\.us/j/[\w?=&-]+', 'Zoom'),
    (r'https://meet\.google\.com/[\w-]+', 'Google Meet'),
    (r'https://teams\.microsoft\.com/l/meetup-join/[\w%/-]+', 'Teams'),
    (r'https://[\w.-]*webex\.com/[\w/.-]+', 'Webex'),
]


def extract_meeting_link(event: "Event") -> tuple[str, str] | None:
    """Extract meeting URL and type from event fields.
    
    Returns (url, meeting_type) or None if no meeting link found.
    """
    text = " ".join(filter(None, [event.notes, event.location, event.url]))
    
    for pattern, meeting_type in MEETING_PATTERNS:
        if match := re.search(pattern, text):
            return (match.group(), meeting_type)
    
    return None


@dataclass
class Event:
    title: str
    start_time: datetime
    end_time: datetime
    notes: str | None = None
    location: str | None = None
    url: str | None = None


class CalendarService:
    def __init__(self):
        self.store = EKEventStore.alloc().init()
        self.config = load_config()
        self.access_granted = False
        self.access_checked = threading.Event()
        self._request_access()

    def _request_access(self):
        def callback(granted, error):
            self.access_granted = granted
            self.access_checked.set()

        self.store.requestAccessToEntityType_completion_(
            EKEntityTypeEvent, callback
        )

    def wait_for_access(self, timeout: float = 30.0) -> bool:
        self.access_checked.wait(timeout)
        return self.access_granted

    def fetch_upcoming_events(self, hours_ahead: int | None = None) -> list[Event]:
        if not self.access_granted:
            return []

        if hours_ahead is None:
            hours_ahead = self.config["lookahead_hours"]

        now = datetime.now(timezone.utc)
        start_date = NSDate.date()
        end_date = NSDate.dateWithTimeIntervalSinceNow_(hours_ahead * 3600)

        calendars = self.store.calendarsForEntityType_(EKEntityTypeEvent)
        predicate = self.store.predicateForEventsWithStartDate_endDate_calendars_(
            start_date, end_date, calendars
        )

        ek_events = self.store.eventsMatchingPredicate_(predicate)
        if not ek_events:
            return []

        events = []
        for ek_event in ek_events:
            event = self._parse_event(ek_event)
            if event:
                events.append(event)

        events.sort(key=lambda e: e.start_time)
        return events

    def _parse_event(self, ek_event) -> Event | None:
        # Skip all-day events
        if ek_event.isAllDay():
            return None

        start_date = ek_event.startDate()
        end_date = ek_event.endDate()

        start_time = datetime.fromtimestamp(
            start_date.timeIntervalSince1970(), tz=timezone.utc
        )
        end_time = datetime.fromtimestamp(
            end_date.timeIntervalSince1970(), tz=timezone.utc
        )

        url = None
        if ek_event.URL():
            url = str(ek_event.URL().absoluteString())

        return Event(
            title=ek_event.title() or "(No title)",
            start_time=start_time,
            end_time=end_time,
            notes=ek_event.notes(),
            location=ek_event.location(),
            url=url,
        )

    def get_next_event(self) -> Event | None:
        events = self.get_upcoming_events(count=1)
        return events[0] if events else None

    def get_upcoming_events(self, count: int = 3) -> list[Event]:
        """Get the next N upcoming events (not in-progress)."""
        now = datetime.now(timezone.utc)
        events = self.fetch_upcoming_events()

        upcoming = []
        for event in events:
            if event.start_time > now:
                upcoming.append(event)
                if len(upcoming) >= count:
                    break

        return upcoming
