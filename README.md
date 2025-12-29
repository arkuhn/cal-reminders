# Cal Reminders

A macOS menubar app that displays a persistent countdown to your next calendar event.

Works with any calendar synced to macOS — Google, iCloud, Outlook, etc. No API keys or OAuth required.

## Install

```bash
git clone https://github.com/<your-username>/cal-reminders
cd cal-reminders
make install
```

Then open the app:
```bash
open '/Applications/Cal Reminders.app'
```

On first launch, grant calendar access when prompted.

## Features

- **Persistent countdown** in menubar: `⏱ 4:32 — Standup`
- **Join button** for Zoom, Google Meet, Teams, and Webex
- **See upcoming events** — next 2-3 meetings at a glance
- **Launch at Login** — never forget to start it
- **Zero configuration** — reads from macOS Calendar

## Screenshot

```
⏱ 4:32 — Standup
─────────────────────────
📅 Standup
   in 4 min · 10:00 - 10:15 AM
🔗 Join Zoom
─────────────────────────
Next up:
   📅 1:1 with Sarah (11:00 AM)
   📅 Team Sync (2:00 PM)
─────────────────────────
Open Calendar
Refresh Now
✓ Launch at Login
─────────────────────────
Quit
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Build and install to /Applications |
| `make build` | Build the .app bundle |
| `make run` | Build and run (for testing) |
| `make dist` | Create zip for distribution |
| `make dev` | Run in development mode |
| `make clean` | Remove build artifacts |

## Configuration

Optional config at `~/.config/cal-reminders/config.json`:

```json
{
  "refresh_interval_seconds": 60,
  "lookahead_hours": 8
}
```

## Requirements

- macOS 12+
- Calendar app configured with your calendars
