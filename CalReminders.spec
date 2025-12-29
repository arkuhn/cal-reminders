# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'rumps',
        'cal_reminders',
        'cal_reminders.calendar',
        'cal_reminders.config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Cal Reminders',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Cal Reminders',
)

app = BUNDLE(
    coll,
    name='Cal Reminders.app',
    icon='assets/icon.icns',
    bundle_identifier='com.cal-reminders.app',
    info_plist={
        'CFBundleName': 'Cal Reminders',
        'CFBundleDisplayName': 'Cal Reminders',
        'CFBundleVersion': '0.2.0',
        'CFBundleShortVersionString': '0.2.0',
        'LSMinimumSystemVersion': '12.0',
        'LSUIElement': True,
        'NSCalendarsUsageDescription': 'Cal Reminders needs calendar access to show countdowns to your upcoming events.',
        'NSHumanReadableCopyright': 'MIT License',
    },
)

