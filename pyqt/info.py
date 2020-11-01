from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

import common
from pyqt.custom_widgets import SquareButton, SquareLabel
from position import Position


class Info(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.board = parent.board

        # Instantiate menu frames
        self.player_frame = PlayerFrame()
        self.move_frame = MoveFrame(self.board)
        self.button_frame = ButtonFrame(self)
        self.computer_frame = ComputerFrame()

        # Add menu frames to vertical box layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.computer_frame, 1)
        layout.addWidget(self.move_frame, 5)
        layout.addWidget(self.button_frame, 1)
        layout.addWidget(self.player_frame, 1)
        self.setLayout(layout)


class ComputerFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('background-color: white')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.font = QFont('Segoe UI', 0, QFont.Bold)  # Font size will be set in resize event

        self.img_label = SquareLabel(QPixmap('./assets/icons/computer.png'))

        self.name_label = QLabel()
        self.name_label.setText('Computer')
        self.name_label.setFont(self.font)
        self.name_label.setStyleSheet('color: grey')

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(self.img_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.font.setPointSize(event.size().width() / 30)
        self.name_label.setFont(self.font)


class MoveFrame(QScrollArea):
    def __init__(self, board):
        super().__init__()

        self.setWidgetResizable(True)

        self.board = board
        self.move_count = 0

        self.setStyleSheet('background-color: white')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)

        for column in range(3):
            self.layout.addWidget(QWidget(), 0, column)
        
        scroll_widget.setLayout(self.layout)
        self.setWidget(scroll_widget)

    def clear_moves(self):
        for move_label in self.findChildren(QLabel):
            move_label.setParent(None)

    def update_moves(self):
        self.clear_moves()
        
        font = QFont()
        font.setBold(True)

        move_history = list(x['move'] for x in self.board.position.undo_info)
        undone_moves = list(reversed(self.board.undone_stack))
        current_move_index = len(move_history) - 1
        
        temp_pos = Position(common.starting_fen)
        
        for index, move in enumerate(move_history + undone_moves):
            # Add move number to frame
            if index % 2 == 0:
                move_num = (index // 2) + 1
                move_num_label = QLabel(str(move_num) + ".")
                move_num_label.setStyleSheet('color: black')
                move_num_label.setFont(font)
                self.layout.addWidget(move_num_label, index // 2, 0)
                column_num = 1
            else:
                column_num = 2

            # Convert move to SAN and add to frame
            san_move = temp_pos.move_to_san(move)
            move_label = QLabel(san_move)
            move_label.setStyleSheet('color: black')
            move_label.setFont(font)
            self.layout.addWidget(move_label, index // 2, column_num)

            # Highlight most recent move
            if index == current_move_index:
                move_label.setStyleSheet('background-color: yellow;'
                                         'color: black')

            # Make move on temporary position
            temp_pos.make_move(move)

        # Process events so that move instantly appears on frame
        QCoreApplication.processEvents()


class ButtonFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.board = parent.board

        self.setStyleSheet('background-color: white')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        reset_pixmap = QPixmap('./assets/icons/reset.png')
        self.reset_btn = SquareButton(reset_pixmap)
        self.reset_btn.clicked.connect(self.reset)

        lightbulb_pixmap = QPixmap('./assets/icons/lightbulb.png')
        self.suggest_move_btn = SquareButton(lightbulb_pixmap)
        self.suggest_move_btn.clicked.connect(self.suggest_move)

        left_arrow_pixmap = QPixmap('./assets/icons/left_arrow.png')
        self.undo_move_btn = SquareButton(left_arrow_pixmap)
        self.undo_move_btn.clicked.connect(self.undo_move)

        right_arrow_pixmap = QPixmap('./assets/icons/right_arrow.png')
        self.redo_move_btn = SquareButton(right_arrow_pixmap)
        self.redo_move_btn.clicked.connect(self.redo_move)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.suggest_move_btn)
        layout.addWidget(self.undo_move_btn)
        layout.addWidget(self.redo_move_btn)
        self.setLayout(layout)

    def enable_buttons(self):
        self.reset_btn.setEnabled(True)
        self.suggest_move_btn.setEnabled(True)
        self.undo_move_btn.setEnabled(True)
        self.redo_move_btn.setEnabled(True)

    def disable_buttons(self):
        self.reset_btn.setEnabled(False)
        self.suggest_move_btn.setEnabled(False)
        self.undo_move_btn.setEnabled(False)
        self.redo_move_btn.setEnabled(False)

    def reset(self):
        self.parent.move_frame.clear_moves()
        self.board.reset()
        self.board.start_game()

    def suggest_move(self):
        if not self.board.position.is_game_over():
            self.disable_buttons()
            self.board.suggest_move()
            self.enable_buttons()

    def undo_move(self):
        if self.board.position.undo_info:
            self.disable_buttons()

            # Undo computer's move
            move = self.board.position.undo_info[-1]['move']  # Get move at the top of move stack
            self.board.move_glide(move, True)  # Move piece back to source square
            self.board.position.undo_move()  # Undo move in game state
            self.board.refresh_from_state()  # Refresh board
            self.board.undone_stack.append(move)

            self.parent.move_frame.update_moves()

            # Undo player's move
            if self.board.position.undo_info:
                move = self.board.position.undo_info[-1]['move'] # Get move at the top of move stack
                self.board.move_glide(move, True)  # Move piece back to source square
                self.board.position.undo_move()  # Undo move in game state
                self.board.refresh_from_state()  # Refresh board
                self.board.undone_stack.append(move)

                self.parent.move_frame.update_moves()
            else:
                self.board.undone_stack.clear()
                self.board.search_thread.start()

            self.board.position.fullmove_number -= 1

            self.enable_buttons()

    def redo_move(self):
        if self.board.undone_stack:
            self.disable_buttons()

            move = self.board.undone_stack.pop()
            self.board.move_glide(move, False)
            self.board.position.make_move(move)
            self.board.refresh_from_state()

            self.parent.move_frame.update_moves()

            move = self.board.undone_stack.pop()
            self.board.move_glide(move, False)
            self.board.position.make_move(move)
            self.board.refresh_from_state()

            self.parent.move_frame.update_moves()

            self.board.position.fullmove_number += 1

            self.enable_buttons()


class PlayerFrame(QFrame):
        def __init__(self):
            super().__init__()

            self.setStyleSheet('background-color: white')
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self.font = QFont('Segoe UI', 0, QFont.Bold)  # Font size will be set in resize event

            self.img_label = SquareLabel(QPixmap('./assets/icons/player.png'))

            self.name_label = QLabel()
            self.name_label.setText('Player')
            self.name_label.setFont(self.font)
            self.name_label.setStyleSheet('color: grey')

            layout = QHBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            layout.addWidget(self.img_label)
            layout.addWidget(self.name_label)
            layout.addStretch()
            self.setLayout(layout)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            self.font.setPointSize(event.size().width() / 30)
            self.name_label.setFont(self.font)
