from setuptools import setup

APP = ['recorder2.py']
DATA_FILES = [
    ('', ['DN-Logo.png'])
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['jira', 'PyQt5', 'qtawesome'],
    'includes': ['charset_normalizer', 'chardet'],
    'iconfile': 'SSHRecorder.icns'  # path to your .icns file

}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
