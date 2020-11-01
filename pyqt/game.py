from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QVBoxLayout, QWidget

from pyqt.board import ChessBoard
from pyqt.custom_widgets import MenuButton
from pyqt.info import Info


class GameFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setStyleSheet('background-color: #4B4945')

        self.user_is_white = True

        self.board = ChessBoard(self)
        self.info = Info(self)

        back_btn = MenuButton()
        back_btn.setText("Back")
        back_btn.clicked.connect(self.back)

        back_widget = QWidget()
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 0, 0, 0)
        back_layout.addWidget(back_btn, 1)
        back_layout.addStretch(6)
        back_widget.setLayout(back_layout)

        game_widget = QWidget()
        game_layout = QHBoxLayout()
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(30)
        game_layout.addWidget(self.board, 8)
        game_layout.addWidget(self.info, 3)
        game_widget.setLayout(game_layout)

        vbox_widget = QWidget()
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(back_widget, 1)
        vbox_layout.addWidget(game_widget, 16)
        vbox_widget.setLayout(vbox_layout)

        self.setLayout(vbox_layout)

    def back(self):
        if self.parent.user and not self.board.saved:
            save_prompt = QMessageBox()
            save_prompt.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
            save_prompt.setIcon(QMessageBox.Warning)
            save_prompt.setWindowTitle("Chess")
            save_prompt.setText("Your current progress will be lost.")
            save_prompt.setInformativeText("Do you want to save the game?")
            save_prompt.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            save_prompt.setDefaultButton(QMessageBox.Save)
            save_prompt.button(QMessageBox.Discard).setText("Don't Save")
            option = save_prompt.exec()

            if option == QMessageBox.Save:  # Save
                self.board.save()
                self.board.search_thread.exit()
                self.parent.stack.setCurrentIndex(0)
            elif option == QMessageBox.Discard:  # Don't save
                self.board.search_thread.exit()
                self.parent.stack.setCurrentIndex(0)
        else:
            self.board.search_thread.exit()
            self.parent.stack.setCurrentIndex(0)

