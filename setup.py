from setuptools import setup

APP = ['recorder.py']
DATA_FILES = [
    ('', ['DN-Logo.png']),
    ('fonts', [
        'fontawesome-free-6.5.1-desktop/otfs/Font Awesome 6 Free-Solid-900.otf',
        # Include any other font files you're using
    ]),
    # If you're using SVG files directly, include them as well
    ('svgs', [
        'fontawesome-free-6.5.1-desktop/svgs/solid/pause.svg',
        'fontawesome-free-6.5.1-desktop/svgs/solid/power-off.svg',
        'fontawesome-free-6.5.1-desktop/svgs/solid/record-vinyl.svg',
        'fontawesome-free-6.5.1-desktop/svgs/solid/stop.svg',
        # Add more if you're using more SVGs
    ]),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PIL', 'jira'],
    'includes': ['charset_normalizer', 'chardet'],
    'iconfile': 'SSHRecorder.icns'  # path to your .icns file

}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
