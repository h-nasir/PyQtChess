from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from pyqt.custom_widgets import ErrorLabel, MenuButton, TextEntry
from user import get_user, username_available


class LoginFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setStyleSheet('background-color: #4B4945')

        back_btn = MenuButton()
        back_btn.setText("Back")
        back_btn.clicked.connect(self.back)

        self.error_label = ErrorLabel()

        self.username_box = TextEntry()
        self.username_box.setPlaceholderText("Username")

        self.password_box = TextEntry()
        self.password_box.setPlaceholderText("Password")
        self.password_box.setEchoMode(QLineEdit.Password)

        login_btn = MenuButton(False)
        login_btn.setText("Sign In")
        login_btn.clicked.connect(self.login)

        back_widget = QWidget()
        back_layout = QVBoxLayout()
        back_layout.setContentsMargins(0, 0, 0, 0)
        back_layout.addWidget(back_btn, 1)
        back_layout.addStretch(16)
        back_widget.setLayout(back_layout)

        entries_widget = QWidget()
        # Vertical box layout holds the entry boxes for the user's details
        entries_layout = QVBoxLayout()
        entries_layout.addStretch(20)
        entries_layout.addWidget(self.error_label, 1)
        entries_layout.addWidget(self.username_box, 1)
        entries_layout.addWidget(self.password_box, 1)
        entries_layout.addStretch(1)
        entries_layout.addWidget(login_btn, 2)
        entries_layout.addStretch(20)
        entries_widget.setLayout(entries_layout)

        hbox_widget = QWidget()
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(back_widget, 1)
        hbox_layout.addStretch(1)
        hbox_layout.addWidget(entries_widget, 2)
        hbox_layout.addStretch(2)
        hbox_widget.setLayout(hbox_layout)

        self.setLayout(hbox_layout)

    def login(self):
        # Get inputs from entry boxes
        username = self.username_box.text()
        password = self.password_box.text()

        # Clear any existing errors
        self.error_label.clear()

        if username_available(username):
            self.error_label.setText("No account with that username")
            return
        else:
            user = get_user(username)
            if user.password == password:
                self.parent.sign_in(user)
            else:
                self.error_label.setText("Incorrect password")
                return

        self.reset()
        self.parent.stack.setCurrentIndex(0)

    def back(self):
        self.reset()
        self.parent.stack.setCurrentIndex(0)

    def reset(self):
        # Clear entry boxes
        self.username_box.clear()
        self.password_box.clear()

        # Clear any errors
        self.error_label.clear()
