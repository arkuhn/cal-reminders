from pathlib import Path
import json

CONFIG_DIR = Path.home() / ".config" / "cal-reminders"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "refresh_interval_seconds": 60,
    "lookahead_hours": 8,
    "enabled_calendars": None,  # None = all calendars enabled
}


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            user_config = json.load(f)
        return {**DEFAULTS, **user_config}
    return DEFAULTS.copy()


def save_config(config: dict) -> None:
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
