from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from pyqt.custom_widgets import ErrorLabel, MenuButton, TextEntry
from user import create_user, get_user, username_available


class RegisterFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setStyleSheet('background-color: #4B4945')

        back_btn = MenuButton()
        back_btn.setText("Back")
        back_btn.clicked.connect(self.back)

        self.username_box = TextEntry()
        self.username_box.setPlaceholderText("Username")

        self.username_error = ErrorLabel()

        self.password_box = TextEntry()
        self.password_box.setPlaceholderText("Password")
        self.password_box.setEchoMode(QLineEdit.Password)

        self.confirm_password_box = TextEntry()
        self.confirm_password_box.setPlaceholderText("Confirm Password")
        self.confirm_password_box.setEchoMode(QLineEdit.Password)

        self.password_error = ErrorLabel()

        register_btn = MenuButton(False)
        register_btn.setText("Register")
        register_btn.clicked.connect(self.register)

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
        entries_layout.addWidget(self.username_box, 1)
        entries_layout.addWidget(self.username_error, 1)
        entries_layout.addWidget(self.password_box, 1)
        entries_layout.addWidget(self.confirm_password_box, 1)
        entries_layout.addWidget(self.password_error, 1)
        entries_layout.addWidget(register_btn, 2)
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

    def register(self):
        # Get inputs from entry boxes
        username = self.username_box.text()
        password = self.password_box.text()
        confirm_password = self.confirm_password_box.text()

        # Clear any existing errors
        self.username_error.clear()
        self.password_error.clear()

        # The following conditions must be met to register for a new account
        if not username:
            self.username_error.setText("Please enter a username")
            return
        elif len(username) > 14:
            self.username_error.setText("Username must be less than 15 characters")
            return
        elif not username_available(username):
            self.username_error.setText("Username not available")
            return
        elif not password:
            self.password_error.setText("Please enter a password")
            return
        elif len(password) < 8:
            self.password_error.setText("Password must be at least 8 characters")
            return
        elif password.isupper() or password.islower():
            self.password_error.setText("Password must contain uppercase and lowercase letters")
            return
        elif not confirm_password:
            self.password_error.setText("Please confirm your password")
            return
        elif password != confirm_password:
            self.password_error.setText("Passwords do not match")
            return

        # Add new user to accounts file
        create_user(username, password)

        # Sign in automatically after registering for new account
        user = get_user(username)
        self.parent.sign_in(user)

        self.reset()
        self.parent.stack.setCurrentIndex(0)

    def back(self):
        self.reset()
        self.parent.stack.setCurrentIndex(0)

    def reset(self):
        # Clear entry boxes
        self.username_box.clear()
        self.password_box.clear()
        self.confirm_password_box.clear()

        # Clear any errors
        self.username_error.clear()
        self.password_error.clear()
