from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget


class MenuImage(QLabel):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)

        pixmap = QPixmap('./assets/icons/crown.png')
        self.setPixmap(pixmap)

        self.setScaledContents(True)


class MenuLabel(QLabel):
    def __init__(self, font_scale=20):
        super().__init__()

        self.font_scale = font_scale

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(150, 50)
        self.setStyleSheet('color: #E6912C')

        self.font = QFont('Segoe UI', 0, QFont.Bold)  # Font size will be set in resizeEvent

    def resizeEvent(self, event):
        # Scale font size relative to label width
        self.font.setPointSize(event.size().width() / self.font_scale)
        self.setFont(self.font)


class MenuButton(QPushButton):
    def __init__(self, scalable=True, font_scale=25):
        super().__init__()

        self.scalable = scalable
        self.font_scale = font_scale

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(150, 50)
        self.setStyleSheet('background-color: #E6912C;'
                           'color: #4B4945')

        self.font = QFont('Segoe UI', 11, QFont.Bold)
        self.setFont(self.font)

    def resizeEvent(self, event):
        # Scale font size relative to button width
        if self.scalable:
            self.font.setPointSize(event.size().width() / self.font_scale)
            self.setFont(self.font)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        self.setStyleSheet('background-color: #D37E19;'
                           'color: #4B4945')

    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.setStyleSheet('background-color: #E6912C;'
                           'color: #4B4945')


class TextEntry(QLineEdit):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('background-color: white')

    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)

    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)


class ErrorLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('color: red')
        self.setFont(QFont('Segoe UI', 6))


class SquareLabel(QLabel):
    def __init__(self, pixmap):
        super().__init__()

        self.setPixmap(pixmap)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)
        self.setScaledContents(True)

    def resizeEvent(self, event):
        if event.size().width() > event.size().height():
            self.resize(event.size().height(), event.size().height())
        else:
            self.resize(event.size().width(), event.size().width())


class SquareButton(QPushButton):
    def __init__(self, pixmap):
        super().__init__()

        self.setStyleSheet('background-color: #DBD9D7')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)

        self.original_pixmap = pixmap
        self.scaled_pixmap = None

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # Leave 2px of space around the pixmap, so button border can be seen
        painter.drawPixmap(2, 2, self.scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if event.size().width() > event.size().height():
            self.resize(event.size().height(), event.size().height())
            pixmap_size = event.size().height() - 4
        else:
            self.resize(event.size().width(), event.size().width())
            pixmap_size = event.size().width() - 4

        # Resize pixmap to 4px less than the new button size, leaving space for a 2px border
        self.scaled_pixmap = self.original_pixmap.scaled(pixmap_size, pixmap_size)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.EnabledChange:
            self.setStyleSheet('background-color: #DBD9D7')

    def enterEvent(self, event):
        if self.isEnabled():
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
            self.setStyleSheet('background-color: #BFBEBA')

    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.setStyleSheet('background-color: #DBD9D7')

