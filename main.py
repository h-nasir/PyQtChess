import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget

from pyqt.menu import MenuFrame
from pyqt.game import GameFrame
from pyqt.multigame import MultiGameFrame
from pyqt.profile import ProfileFrame
from pyqt.register import RegisterFrame
from pyqt.login import LoginFrame
from user import update_user


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget(self)

        self.user = None

        # Instantiate frames for different pages
        self.main_menu = MenuFrame(self)
        self.game_frame = GameFrame(self)
        self.multigame_frame = MultiGameFrame(self)
        self.profile_frame = ProfileFrame(self)
        self.register_frame = RegisterFrame(self)
        self.login_frame = LoginFrame(self)

        # Insert frames into a stack
        self.stack.insertWidget(0, self.main_menu)
        self.stack.insertWidget(1, self.game_frame)
        self.stack.insertWidget(2, self.profile_frame)
        self.stack.insertWidget(3, self.register_frame)
        self.stack.insertWidget(4, self.login_frame)
        self.stack.insertWidget(5, self.multigame_frame)

        # Set current frame to main menu
        self.stack.setCurrentIndex(0)

        # Set window details
        self.setCentralWidget(self.stack)
        self.setWindowTitle("Chess")
        self.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
        self.setMinimumSize(1600, 900)
        self.showMaximized()
        
    def closeEvent(self, event):
        if self.user:
            update_user(self.user)  # On close, update user wins/losses/draws
            if self.stack.currentIndex() == 1 and not self.game_frame.board.saved:
                save_prompt = QMessageBox()
                save_prompt.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
                save_prompt.setIcon(QMessageBox.Warning)
                save_prompt.setWindowTitle("Chess")
                save_prompt.setText("Your current progress will be lost.")
                save_prompt.setInformativeText("Do you want to save the game?")
                save_prompt.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                save_prompt.setDefaultButton(QMessageBox.Save)
                save_prompt.button(QMessageBox.Discard).setText("Don't Save")
                option = save_prompt.exec_()

                # Save
                if option == QMessageBox.Save:
                    self.game_frame.board.save()
                    event.accept()
                # Don't save
                elif option == QMessageBox.Discard:
                    event.accept()
                # Cancel
                else:
                    event.ignore()

    def sign_in(self, user):
        self.user = user
        self.main_menu.name_label.setText(user.username)
        self.main_menu.bottom_left_stack.setCurrentIndex(1)
        self.main_menu.bottom_right_stack.setCurrentIndex(1)

    def sign_out(self):
        self.user = None
        self.main_menu.bottom_left_stack.setCurrentIndex(0)
        self.main_menu.bottom_right_stack.setCurrentIndex(0)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())  # Start main event loop
