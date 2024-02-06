import datetime
import os
import sys
import traceback

import qtawesome as qta
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, \
    QSpacerItem, QSizePolicy, QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt, QCoreApplication

import subprocess

from write import SSHRecorder, SOURCE_PATH


version = "1.4.4"
date = "6-Feb-2024"


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.dialog = None
        self.recording_started = None
        self._recorder = None
        self.exit_button = None
        self.status_label = None
        self.stop_button = None
        self.record_button = None
        self.text_entry = None
        self.pause_button = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSH Recorder")
        self.setGeometry(100, 100, 350, 300)  # Adjust the size as needed
        self.setFixedSize(440, 300)

        # Create layout managers
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        entry_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        status_layout = QHBoxLayout()

        # Logo label
        logo_pixmap = QPixmap("./DN-Logo.png").scaled(200, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label = QLabel(self)
        logo_label.setPixmap(logo_pixmap)

        # Title label
        title_label = QLabel("SSH Recorder", self)
        title_label.setStyleSheet("color: '#2050FF'; font-size: 30px; font-weight: bold;")

        # Add logo and title to the header layout
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()  # This will push the logo and title to the left

        # Jira ticket number entry
        entry_label = QLabel("Jira ticket number:", self)
        entry_label.setStyleSheet("font-size: 15px;")
        self.text_entry = QLineEdit(self)
        self.text_entry.setStyleSheet("font-size: 15px;")
        self.text_entry.setMaximumWidth(150)
        self.text_entry.textChanged.connect(self.entry_callback)  # Connect signal to slot
        entry_layout.addWidget(entry_label)
        entry_layout.addWidget(self.text_entry)

        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        entry_layout.addItem(vertical_spacer)

        # Record button with Font Awesome icon
        self.record_button = QPushButton(qta.icon('fa5s.record-vinyl', color='red'), '', self)
        self.record_button.setIconSize(QSize(25, 25))
        self.record_button.setFixedSize(40, 40)
        self.record_button.clicked.connect(self.start_resume_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.record_button)

        # Pause button with Font Awesome icon
        self.pause_button = QPushButton(qta.icon('fa5s.pause', color='#FFC107'), '', self)
        self.pause_button.setIconSize(QSize(25, 25))
        self.pause_button.setFixedSize(40, 40)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.pause_button)

        # Stop button with Font Awesome icon
        self.stop_button = QPushButton(qta.icon('fa5s.stop', color='red'), '', self)
        self.stop_button.setIconSize(QSize(25, 25))
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.stop_button)

        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        buttons_layout.addItem(vertical_spacer)

        # Status label
        self.status_label = QLabel("Status: Idle", self)
        self.status_label.setStyleSheet("font-size: 10px;")
        status_layout.addWidget(self.status_label)

        # version label
        version_label = QLabel(f"Version: {version}\nDate: {date}", self)
        version_label.setStyleSheet("font-size: 10px;")
        status_layout.addWidget(version_label)

        self.exit_button = QPushButton(qta.icon('fa5s.power-off', color='red'), '', self)
        self.exit_button.setIconSize(QSize(20, 20))
        self.exit_button.setFixedSize(30, 30)
        self.exit_button.clicked.connect(self.close)  # Uncomment when function is defined
        status_layout.addWidget(self.exit_button)

        # Adding widgets to the main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(entry_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(status_layout)

        # Set the main layout to the window
        self.setLayout(main_layout)
        self.entry_callback()  # Disable record button by default
        self.apply_dark()
        self.repaint()
        self.update()
        self.append_script_to_zshrc('script.txt')

    def entry_callback(self):
        text = self.text_entry.text().strip()
        if text:
            self.record_button.setEnabled(True)
        else:
            self.record_button.setEnabled(False)

    @property
    def recorder(self):
        """
        get the SSHRecorder object
        :return:
        """
        if self._recorder is None:
            self._recorder = SSHRecorder()
        return self._recorder

    def start_resume_recording(self):
        """
        start/resume recording the SSH session
        :return:
        """
        if self.recording_started:
            self.recorder.resume_recording()
        else:
            if self.recorder.validate_jira_ticket(self.text_entry.text()):
                self.recorder.start_recording()
                self.recording_started = True
                self.text_entry.setEnabled(False)
            else:
                self.status_label.setText("Status: Invalid Jira ticket")
                self.text_entry.setText("")
                return
        self.record_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Recording")

    def pause_recording(self):
        """
        pause recording the SSH session
        :return:
        """
        self.recorder.pause_recording()
        self.record_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.status_label.setText("Status: Paused    ")

    def stop_recording(self):
        """
        stop recording the SSH session
        :return:
        """
        # Create a custom dialog
        self.dialog = StopRecordingDialog(self)
        self.dialog.exec_()  # This will run the dialog in modal form

    def confirm_stop_upload(self):
        """
        stop recording the SSH session and upload to jira
        :return:
        """
        # upload to jira
        self.close_helper()
        result = self.recorder.upload_to_jira()
        if result:
            self.status_label.setText("Status: Upload successful")
        else:
            self.status_label.setText("Status: Nothing to upload")
        self._recorder = None
        self.record_button.setEnabled(False)
        self.text_entry.setText("")

    def confirm_stop_no_upload(self):
        """
        stop recording the SSH session
        :return:
        """
        self.close_helper()
        self._recorder = None
        self.record_button.setEnabled(True)
        self.status_label.setText("Status: Nothing to upload")

    def close_helper(self):
        """
        close the dialog helper
        :return:
        """
        self.recording_started = False
        self.recorder.stop_recording()
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.text_entry.setEnabled(True)
        self.dialog.accept()

    @staticmethod
    def append_script_to_zshrc(script_file_path, zshrc_path='~/.zshrc'):
        # Expand the user's home directory (~)
        zshrc_path = os.path.expanduser(zshrc_path)
        start_marker = "# Appended script\n"
        end_marker = "# End appended script\n"

        try:
            # Read the script from the file
            with open(script_file_path, 'r') as script_file:
                script_content = script_file.read()

            # Read the existing .zshrc content
            if os.path.isfile(zshrc_path):
                with open(zshrc_path, 'r') as zshrc_file:
                    zshrc_content = zshrc_file.readlines()
                    if script_content in "".join(zshrc_content):
                        return  # Script already exists in ~/.zshrc
            else:
                zshrc_content = []

            # Remove old script content if it exists
            start_index = None
            end_index = None
            for i, line in enumerate(zshrc_content):
                if start_marker in line:
                    start_index = i
                elif end_marker in line:
                    end_index = i + 1
                    break
            if start_index is not None:
                del zshrc_content[start_index:end_index]

            # Append new script content
            with open(zshrc_path, 'w') as zshrc_file:
                zshrc_file.writelines(zshrc_content)
                zshrc_file.write(start_marker)
                zshrc_file.write(script_content)
                zshrc_file.write('\n')
                zshrc_file.write(end_marker)

            print("Script updated successfully in ~/.zshrc")
            os.system("osascript -e 'tell application \"iTerm\" to quit without saving'")

        except Exception as e:
            print(f"Error updating script in ~/.zshrc: {e}")

    def closeEvent(self, event):
        """
        override the closeEvent method to handle any cleanup
        :param event: The event object
        :return:
        """
        # handle any cleanup here
        event.accept()  # or event.ignore() if there's a reason to stop the closure

    @staticmethod
    def apply_dark():
        """
        apply dark theme styles
        """
        button_style = """
            QPushButton {{
                border: 2px solid #8f8f91;
                background-color: {background};  /* Darker background for dark theme */
                color: {button_text_color};  /* Light text for dark theme */
                border-style: outset;
            }}
            QPushButton:hover {{
                background-color: {foreground};
            }}
            QPushButton:pressed {{
                background-color: {foreground};
                border-style: inset;
            }}
        """
        text_area_style = """
            QLineEdit, QTextEdit{{
                background-color: {background};
                color: {foreground};
                border: 1px solid #8f8f91;
            }}
        """
        qlabel_style = """
            QLabel {{
                color: {foreground};
            }}
        """

        main_window_style = "QWidget {{ background-color: {background}; }}"
        theme = App.get_macos_theme()
        if theme == 'Dark':
            # Dark theme styles
            background = '#333333'  # Dark background color
            foreground = '#EEEEEE'  # Light text color
            button_background = '#555555'  # Darker background for dark theme
            button_pushed = '#777777'
            button_text_color = '#EEEEEE'  # Light text for dark theme

        else:
            # Light theme styles
            background = '#FFFFFF'
            foreground = '#707070'
            button_background = '#EEEEEE'
            button_pushed = '#CCCCCC'
            button_text_color = '#333333'

        text_area_style = text_area_style.format(background=background, foreground=foreground)
        main_window_style = main_window_style.format(background=background)
        button_style = button_style.format(background=button_background, foreground=button_pushed,
                                           button_text_color=button_text_color)
        qlabel_style = qlabel_style.format(foreground=foreground)

        # Apply the styles
        combined_styles = main_window_style + text_area_style + button_style + qlabel_style
        QApplication.instance().setStyleSheet(combined_styles)

    @staticmethod
    def get_macos_theme():
        try:
            theme = subprocess.check_output(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            # The command above will raise an error if the theme is set to light,
            # as the 'AppleInterfaceStyle' key will not exist.
            theme = 'Light'

        return theme  # Will return 'Dark' or 'Light'


class StopRecordingDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Stop Recording")

        # Set up the layout
        layout = QVBoxLayout(self)

        # Add dialog message
        label = QLabel("Do you want to stop the recording and upload the results?")
        layout.addWidget(label)

        # Set up the buttons
        buttons_layout = QHBoxLayout()

        # Button for "Stop and Upload to Jira"
        upload_button = QPushButton("Stop and Upload to Jira")
        upload_button.clicked.connect(parent.confirm_stop_upload)
        buttons_layout.addWidget(upload_button)

        # Button for "Stop but Don't Upload"
        no_upload_button = QPushButton("Stop but Don't Upload")
        no_upload_button.clicked.connect(parent.confirm_stop_no_upload)
        buttons_layout.addWidget(no_upload_button)

        # Button for "Cancel"
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.accept)
        buttons_layout.addWidget(cancel_button)

        # Add the buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set dialog modality
        self.setModal(True)
        App.apply_dark()


class CrashDialog(QDialog):
    """
    This dialog shows up when a crash occurs
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crash Detected")

        # Set up the layout
        layout = QVBoxLayout(self)

        # Add dialog message
        label = QLabel(f"Unfortunately a crash happened. \nA log file was created in {SOURCE_PATH}err_log.txt\n Please send it to the developer.")
        layout.addWidget(label)

        # Set up the buttons
        buttons_layout = QHBoxLayout()

        # Button for "Stop and Upload to Jira"
        crash_button = QPushButton("OK")
        crash_button.clicked.connect(self.close)
        buttons_layout.addWidget(crash_button)

        # Add the buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set dialog modality
        self.setModal(True)
        App.apply_dark()


def log_uncaught_exceptions(ex_cls, ex, tb):
    """
    log uncaught exceptions
    :param ex_cls: Exception class
    :param ex: Exception
    :param tb: traceback
    """
    error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f"{SOURCE_PATH}error_log.txt", "w") as log_file:
        log_file.write(f"\n{error_time} - Uncaught Exception:\n")
        log_file.write(f"{ex_cls.__name__}: {ex}\n")
        traceback.print_tb(tb, file=log_file)

    dialog = CrashDialog(exx)
    dialog.exec_()
    QCoreApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    exx = App()
    sys.excepthook = log_uncaught_exceptions
    exx.show()
    sys.exit(app.exec_())
