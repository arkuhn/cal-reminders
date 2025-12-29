#!/usr/bin/env python3
"""Entry point for PyInstaller bundle."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from cal_reminders.app import main

if __name__ == "__main__":
    main()

