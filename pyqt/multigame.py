from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QMessageBox, QVBoxLayout, QWidget

from pyqt.board import ChessBoard
from pyqt.custom_widgets import MenuButton
from pyqt.info import Info

import common

class MultiGameFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.colsCount = 3
        self.rowsCount = 2
        self.gridCount = self.colsCount * self.rowsCount

        self.setStyleSheet('background-color: #4B4945')

        self.user_is_white = True

        self.board = []
        self.info = []
        for i in range(self.gridCount):
            self.board.append(ChessBoard(self))
            self.info.append(Info(self))
            self.board[i].setInfo(self.info[i])
            self.info[i].setBoard(self.board[i])

        back_btn = MenuButton()
        back_btn.setText("Back")
        back_btn.clicked.connect(self.back)

        back_widget = QWidget()
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 0, 0, 0)
        back_layout.addWidget(back_btn, 1)
        back_layout.addStretch(6)
        back_widget.setLayout(back_layout)

        grid_layout = QGridLayout()

        for i in range(self.gridCount):
            game_widget = QWidget()
            game_layout = QHBoxLayout()
            game_layout.setContentsMargins(0, 0, 0, 0)
            game_layout.addWidget(self.board[i], 8)
            game_layout.addWidget(self.info[i], 3)
            game_widget.setLayout(game_layout)

            grid_layout.addWidget(game_widget,
                                  int(i / self.colsCount),
                                  int(i % self.colsCount))

        vbox_widget = QWidget()
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(back_widget, 1)
        vbox_layout.addLayout(grid_layout, 16)
        vbox_widget.setLayout(vbox_layout)

        self.setLayout(vbox_layout)

    def back(self):
        for i in range(self.gridCount):
            self.board[i].search_thread.exit()
        self.parent.stack.setCurrentIndex(0)

    def clear_moves(self):
        for i in range(self.gridCount):
            self.info[i].move_frame.clear_moves()

    def start_game(self, colour, difficulty, autosave, self_play):
        for i in range(self.gridCount):
            self.board[i].set_fen(common.starting_fen)
            self.board[i].user_is_white = True if colour == 'w' else False
            self.board[i].self_play = self_play
            self.board[i].difficulty = difficulty
            self.board[i].autosave = autosave
            self.board[i].start_game()


