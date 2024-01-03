import os
import sys
import qtawesome as qta
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, \
    QSpacerItem, QSizePolicy, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

from write import SSHRecorder

style = """
            QPushButton {
                border: 2px solid #8f8f91;  /* Two pixels width black border */
                background-color: #EEEEEE;  /* Change text color as needed */
                border-style: outset;  /* Make it look like pressed */
            }
            QPushButton:hover {
                background-color: #CCCCCC;  /* Slightly darker shade when hovered */
            }
            QPushButton:pressed {
                background-color: #CCCCCC;  /* Even darker shade when pressed */
                border-style: inset;  /* Make the border look inset */
            }
        """

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
        self.setFixedSize(420, 300)
        self.setStyleSheet("background-color: white;")

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
        title_label.setStyleSheet("color: blue; font-size: 30px;")

        # Add logo and title to the header layout
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()  # This will push the logo and title to the left

        # Jira ticket number entry
        entry_label = QLabel("Jira ticket number:", self)
        entry_label.setStyleSheet("color: gray; font-size: 15px;")
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
        self.record_button.setStyleSheet(style)
        self.record_button.clicked.connect(self.start_resume_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.record_button)

        # Pause button with Font Awesome icon
        self.pause_button = QPushButton(qta.icon('fa5s.pause', color='#FFC107'), '', self)
        self.pause_button.setIconSize(QSize(25, 25))
        self.pause_button.setFixedSize(40, 40)
        self.pause_button.setStyleSheet(style)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.pause_button)

        # Stop button with Font Awesome icon
        self.stop_button = QPushButton(qta.icon('fa5s.stop', color='red'), '', self)
        self.stop_button.setIconSize(QSize(25, 25))
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setStyleSheet(style)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.stop_button)

        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        buttons_layout.addItem(vertical_spacer)

        # Status label
        self.status_label = QLabel("Status: Idle", self)
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        status_layout.addWidget(self.status_label)

        self.exit_button = QPushButton(qta.icon('fa5s.power-off', color='red'), '', self)
        self.exit_button.setIconSize(QSize(20, 20))
        self.exit_button.setFixedSize(30, 30)
        self.exit_button.setStyleSheet(style)
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
        self.dialog = StopRecordingDialog(self.confirm_stop_upload, self.confirm_stop_no_upload, self)
        self.dialog.exec_()  # This will run the dialog in modal form

    def confirm_stop_upload(self):
        """
        stop recording the SSH session and upload to jira
        :return:
        """
        # upload to jira
        self.close_helper()
        self.recorder.upload_to_jira()
        self._recorder = None

    def confirm_stop_no_upload(self):
        """
        stop recording the SSH session
        :return:
        """
        self.close_helper()
        self._recorder = None

    def close_helper(self):
        """
        close the dialog helper
        :return:
        """
        self.recording_started = False
        self.recorder.stop_recording()
        self.record_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.text_entry.setEnabled(True)
        self.status_label.setText("Status: Idle")
        self.text_entry.setText("")
        self.dialog.accept()

    @staticmethod
    def append_script_to_zshrc(script_file_path, zshrc_path='~/.zshrc'):
        # Expand the user's home directory (~)
        zshrc_path = os.path.expanduser(zshrc_path)

        try:
            # Read the script from the file
            with open(script_file_path, 'r') as script_file:
                script_content = script_file.read()

            # Check if the script content is already in ~/.zshrc
            if not os.path.isfile(zshrc_path):
                # create the file if it doesn't exist
                open(zshrc_path, 'w').close()
            with open(zshrc_path, 'r') as zshrc_file:
                if script_content in zshrc_file.read():
                    print("Script is already in ~/.zshrc")
                    return

            # Append the script content to ~/.zshrc
            with open(zshrc_path, 'a') as zshrc_file:
                zshrc_file.write('\n# Appended script\n')
                zshrc_file.write(script_content)

            print("Script appended successfully to ~/.zshrc")
            os.system("osascript -e 'tell application \"iTerm\" to quit without saving'")

        except Exception as e:
            print(f"Error appending script to ~/.zshrc: {e}")

    def closeEvent(self, event):
        """
        override the closeEvent method to handle any cleanup
        :param event: The event object
        :return:
        """
        # handle any cleanup here
        event.accept()  # or event.ignore() if there's a reason to stop the closure

class StopRecordingDialog(QDialog):
    def __init__(self, confirm_stop_upload, confirm_stop_no_upload, parent=None):
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
        upload_button.clicked.connect(confirm_stop_upload)
        buttons_layout.addWidget(upload_button)

        # Button for "Stop but Don't Upload"
        no_upload_button = QPushButton("Stop but Don't Upload")
        no_upload_button.clicked.connect(confirm_stop_no_upload)
        buttons_layout.addWidget(no_upload_button)

        # Button for "Cancel"
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.accept)
        buttons_layout.addWidget(cancel_button)

        # Add the buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set dialog modality
        self.setModal(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
