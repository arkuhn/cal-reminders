.PHONY: install build clean dev run

# Install uv if not present, then build and install the app
install: build
	@echo "Installing to /Applications..."
	@rm -rf "/Applications/Cal Reminders.app"
	@cp -r "dist/Cal Reminders.app" /Applications/
	@echo "✓ Installed to /Applications/Cal Reminders.app"
	@echo "Run: open '/Applications/Cal Reminders.app'"

# Build the .app bundle
build: check-uv
	@echo "Building Cal Reminders.app..."
	@uv sync
	@uv run pyinstaller CalReminders.spec --noconfirm --log-level WARN
	@echo "✓ Built: dist/Cal Reminders.app"

# Create distributable zip
dist: build
	@echo "Creating distribution zip..."
	@cd dist && zip -rq "Cal-Reminders-mac.zip" "Cal Reminders.app"
	@echo "✓ Created: dist/Cal-Reminders-mac.zip"

# Run the app (for testing)
run: build
	@open "dist/Cal Reminders.app"

# Development mode - run without building .app
dev: check-uv
	@uv sync
	@uv run cal-reminders

# Clean build artifacts
clean:
	@rm -rf build dist __pycache__ *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

# Check if uv is installed
check-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "Run 'source ~/.local/bin/env' then try again"; \
		exit 1; \
	}
