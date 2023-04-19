import copy

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QCheckBox, QDialog, QFrame, QHBoxLayout, QMessageBox, QSlider, QStackedWidget, QVBoxLayout, QWidget

import common
from pyqt.custom_widgets import MenuButton, MenuImage, MenuLabel


class MenuFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setStyleSheet('background-color: #4B4945')

        menu_img = MenuImage()

        img_widget = QWidget()
        # Horizontal box layout used to add space to both sides of the image
        img_layout = QHBoxLayout()
        img_layout.addStretch(1)
        img_layout.addWidget(menu_img, 2)
        img_layout.addStretch(1)
        img_widget.setLayout(img_layout)

        new_game_btn = MenuButton()
        new_game_btn.setText("New Game")
        new_game_btn.clicked.connect(self.open_dialog)

        new_multigame_btn = MenuButton()
        new_multigame_btn.setText("Start Multiple Games")
        new_multigame_btn.clicked.connect(lambda: self.open_dialog(False, True))

        load_game_btn = MenuButton()
        load_game_btn.setText("Load Game")
        load_game_btn.clicked.connect(lambda: self.open_dialog(True))

        profile_btn = MenuButton()
        profile_btn.setText("Profile")
        profile_btn.clicked.connect(self.profile_page)

        exit_btn = MenuButton()
        exit_btn.setText("Exit")
        exit_btn.clicked.connect(self.exit)

        button_widget = QWidget()
        # Vertical box layout used to hold the image widget and buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(img_widget, 2)
        button_layout.addWidget(new_game_btn, 1)
        button_layout.addWidget(new_multigame_btn, 1)
        button_layout.addWidget(load_game_btn, 1)
        button_layout.addWidget(profile_btn, 1)
        button_layout.addWidget(exit_btn, 1)
        button_widget.setLayout(button_layout)

        register_btn = MenuButton()
        register_btn.setText("Register")
        register_btn.clicked.connect(self.register_page)

        login_btn = MenuButton()
        login_btn.setText("Log In")
        login_btn.clicked.connect(self.login_page)

        self.name_label = MenuLabel()

        logout_btn = MenuButton()
        logout_btn.setText("Sign out")
        logout_btn.clicked.connect(self.parent.sign_out)

        self.bottom_left_stack = QStackedWidget()
        self.bottom_left_stack.insertWidget(0, register_btn)
        self.bottom_left_stack.insertWidget(1, self.name_label)
        self.bottom_left_stack.setCurrentIndex(0)

        self.bottom_right_stack = QStackedWidget()
        self.bottom_right_stack.insertWidget(0, login_btn)
        self.bottom_right_stack.insertWidget(1, logout_btn)
        self.bottom_right_stack.setCurrentIndex(0)

        register_widget = QWidget()
        # Vertical box layout used to position the register button
        register_layout = QVBoxLayout()
        register_layout.addStretch(15)
        register_layout.addWidget(self.bottom_left_stack, 1)
        register_widget.setLayout(register_layout)

        login_widget = QWidget()
        # Vertical box layout used to position the login button
        login_layout = QVBoxLayout()
        login_layout.addStretch(15)
        login_layout.addWidget(self.bottom_right_stack, 1)
        login_widget.setLayout(login_layout)

        # Horizontal box layout used to add space to both sides of the image widget and buttons
        menu_layout = QHBoxLayout()
        menu_layout.addWidget(register_widget, 1)
        menu_layout.addStretch(1)
        menu_layout.addWidget(button_widget, 2)
        menu_layout.addStretch(1)
        menu_layout.addWidget(login_widget, 1)
        self.setLayout(menu_layout)

    def open_dialog(self, load_game=False, is_multiple=False):
        if load_game:
            if not self.parent.user or not self.parent.user.saved_game:
                info_message = QMessageBox()
                info_message.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
                info_message.setIcon(QMessageBox.Warning)
                info_message.setWindowTitle("Chess")
                info_message.setText("There are no saved games")
                info_message.setInformativeText("Please start a new one")
                info_message.setStandardButtons(QMessageBox.Ok)
                info_message.setDefaultButton(QMessageBox.Ok)
                info_message.exec_()
                return
            target_func = self.load_game
        else:
            target_func = self.new_game

        if is_multiple:
            target_func = self.new_multigame

        bold_font = QFont()
        bold_font.setBold(True)

        menu = QDialog()
        menu.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
        menu.setWindowTitle("Chess")
        menu.setStyleSheet('background-color: #4B4945')

        white_btn = MenuButton()
        white_btn.setText("White")
        white_btn.clicked.connect(menu.accept)

        black_btn = MenuButton()
        black_btn.setText("Black")
        black_btn.clicked.connect(menu.accept)

        player_btn_widget = QWidget()
        player_btn_layout = QHBoxLayout()
        player_btn_layout.addWidget(white_btn)
        player_btn_layout.addWidget(black_btn)
        player_btn_widget.setLayout(player_btn_layout)

        computer_btn = MenuButton(font_scale=40)
        computer_btn.setText("Computer vs Computer")
        computer_btn.clicked.connect(menu.accept)

        computer_btn_widget = QWidget()
        computer_btn_layout = QHBoxLayout()
        computer_btn_layout.addWidget(computer_btn)
        computer_btn_widget.setLayout(computer_btn_layout)

        slider_label = MenuLabel(font_scale=35)
        slider_label.setText("Difficulty")

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(5)
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setStyleSheet('QSlider::handle:horizontal {background-color: #E6912C}'
                             'QSlider::handle:horizontal:hover {background-color: #D37E19}')

        checkbox = QCheckBox()
        checkbox.setText("Enable autosave")
        checkbox.setFont(bold_font)
        checkbox.setStyleSheet('QCheckBox {color: #E6912C}')

        white_btn.clicked.connect(lambda: target_func('w', slider.value(), checkbox.isChecked(), False))
        black_btn.clicked.connect(lambda: target_func('b', slider.value(), checkbox.isChecked(), False))
        computer_btn.clicked.connect(lambda: target_func(None, slider.value(), checkbox.isChecked(), True))

        layout = QVBoxLayout()
        layout.addWidget(player_btn_widget)
        layout.addWidget(computer_btn_widget)
        layout.addWidget(slider_label)
        layout.addWidget(slider)
        if self.parent.user:
            layout.addSpacing(40)
            layout.addWidget(checkbox)
        layout.setSpacing(0)
        menu.setLayout(layout)

        menu.exec_()

    def new_game(self, colour, difficulty, autosave, self_play):
        self.parent.game_frame.info.move_frame.clear_moves()
        self.parent.game_frame.board.set_fen(common.starting_fen)
        self.parent.game_frame.board.user_is_white = True if colour == 'w' else False
        self.parent.game_frame.board.self_play = self_play
        self.parent.game_frame.board.difficulty = difficulty
        self.parent.game_frame.board.autosave = autosave
        self.parent.game_frame.board.start_game()
        self.parent.stack.setCurrentIndex(1)

    def new_multigame(self, colour, difficulty, autosave, self_play):
        self.parent.multigame_frame.clear_moves()
        self.parent.multigame_frame.start_game(
            colour,
            difficulty,
            autosave,
            self_play)
        self.parent.stack.setCurrentIndex(5)

    def load_game(self, colour, difficulty, autosave, self_play):
        self.parent.game_frame.board.set_position(copy.deepcopy(self.parent.user.saved_game))
        self.parent.game_frame.board.saved = True
        self.parent.game_frame.info.move_frame.update_moves()
        self.parent.game_frame.board.user_is_white = True if colour == 'w' else False
        self.parent.game_frame.board.self_play = self_play
        self.parent.game_frame.board.difficulty = difficulty
        self.parent.game_frame.board.autosave = autosave
        self.parent.game_frame.board.start_game()
        self.parent.stack.setCurrentIndex(1)

    def profile_page(self):
        if self.parent.user:
            self.parent.profile_frame.update()
            self.parent.stack.setCurrentIndex(2)

    def exit(self):
        self.parent.close()

    def register_page(self):
        self.parent.stack.setCurrentIndex(3)

    def login_page(self):
        self.parent.stack.setCurrentIndex(4)
