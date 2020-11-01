from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from pyqt.custom_widgets import MenuButton, MenuLabel


class ProfileFrame(QFrame):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setStyleSheet('background-color: #4B4945')

        back_btn = MenuButton()
        back_btn.setText("Back")
        back_btn.clicked.connect(self.back)

        self.wins_label = MenuLabel()
        self.losses_label = MenuLabel()
        self.draws_label = MenuLabel()
        self.win_percent_label = MenuLabel(30)

        back_widget = QWidget()
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 0, 0, 0)
        back_layout.addWidget(back_btn, 1)
        back_layout.addStretch(6)
        back_widget.setLayout(back_layout)

        labels_widget = QWidget()
        labels_layout = QVBoxLayout()
        labels_layout.addWidget(self.wins_label, 1)
        labels_layout.addWidget(self.losses_label, 1)
        labels_layout.addWidget(self.draws_label, 1)
        labels_layout.addStretch(1)
        labels_layout.addWidget(self.win_percent_label, 1)
        labels_widget.setLayout(labels_layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axis = self.figure.add_subplot(111)
        
        stats_widget = QWidget()
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(labels_widget, 3)
        stats_layout.addWidget(self.canvas, 7)
        stats_widget.setLayout(stats_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(back_widget, 1)
        main_layout.addWidget(stats_widget, 16)

        self.setLayout(main_layout)

    def update(self):
        wins = self.parent.user.wins
        losses = self.parent.user.losses
        draws = self.parent.user.draws
        total = wins + losses + draws

        if total > 0:
            win_percent = (wins / total) * 100
        else:
            win_percent = 0

        self.parent.profile_frame.wins_label.setText("Wins: {}".format(wins))
        self.parent.profile_frame.losses_label.setText("Losses: {}".format(losses))
        self.parent.profile_frame.draws_label.setText("Draws: {}".format(draws))
        self.parent.profile_frame.win_percent_label.setText("Win Percentage: {:.1f}%".format(win_percent))

        self.axis.clear()
        self.axis.plot(self.parent.user.history, color='#E6912C', marker='.')
        self.parent.profile_frame.canvas.draw()
        self.axis.set_xlim(xmin=0)
        self.axis.set_ylim(0, 100)
        self.axis.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.axis.set_xlabel('Games Played')
        self.axis.set_ylabel('Win Percentage')

    def back(self):
        # Switch to main menu
        self.parent.stack.setCurrentIndex(0)

