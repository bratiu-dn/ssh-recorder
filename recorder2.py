import sys
import qtawesome as qta
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, \
    QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt


class App(QWidget):
    def __init__(self):
        super().__init__()
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
        entry_layout.addWidget(entry_label)
        entry_layout.addWidget(self.text_entry)

        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        entry_layout.addItem(vertical_spacer)

        # Record button with Font Awesome icon
        self.record_button = QPushButton(qta.icon('fa5s.circle', color='red'), '', self)
        self.record_button.setIconSize(QSize(25, 25))
        self.record_button.setFixedSize(40, 40)
        # self.record_button.clicked.connect(self.start_resume_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.record_button)

        # Pause button with Font Awesome icon
        self.pause_button = QPushButton(qta.icon('fa5s.pause', color='#FFC107'), '', self)
        self.pause_button.setIconSize(QSize(25, 25))
        self.pause_button.setFixedSize(40, 40)
        # self.pause_button.clicked.connect(self.pause_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.pause_button)

        # Stop button with Font Awesome icon
        self.stop_button = QPushButton(qta.icon('fa5s.stop', color='#F44336'), '', self)
        self.stop_button.setIconSize(QSize(25, 25))
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setStyleSheet("""
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
        """)

        self.stop_button.clicked.connect(self.stop_recording)  # Uncomment when function is defined
        buttons_layout.addWidget(self.stop_button)

        # Status label
        self.status_label = QLabel("Status: Idle", self)
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")

        # Adding widgets to the main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(entry_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.status_label)

        # Set the main layout to the window
        self.setLayout(main_layout)

    def entry_callback(self):
        text = self.text_entry.text().strip()
        if text:
            self.record_button.setEnabled(True)
        else:
            self.record_button.setEnabled(False)

    def start_resume_recording(self):
        print("Start or resume recording")
        # Add functionality to start/resume recording

    def pause_recording(self):
        print("Pause recording")
        # Add functionality to pause recording

    def stop_recording(self):
        print("Stop recording")
        # Add functionality to stop recording


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
