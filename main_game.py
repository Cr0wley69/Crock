import sys

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QLabel, QLineEdit


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gameplayDesign.ui', self)
        self._im = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_ARGB32)
        self._im.fill(QtGui.QColor("white"))
        self.color = (0, 0, 0)

        self.wht.setStyleSheet("QPushButton {background-color: white; border-style: outset; border-width: 2px; "
                          "border-radius: 15px; border-color: black;padding: 4px;}")
        self.wht.clicked.connect(self.white)
        self.blc.setStyleSheet("QPushButton {background-color: black; border-style: outset; border-width: 2px; "
                               "border-radius: 15px; border-color: black;padding: 4px;}")
        self.blc.clicked.connect(self.black)
        self.pen_size = 5
        self.size_text.setText('Размер ручки')
        self.combo.addItems(["1", "2", "3", "4"])

        self.mistery = "Дунаев"
        self.combo.activated.connect(self.change_size)
        self.sendButton.clicked.connect(self.check)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super().mouseReleaseEvent(event)
        if 160 <= event.x() <= 120 + 601 and 60 <= event.y() <= 380:
            painter = QtGui.QPainter(self._im)
            painter.setPen(QtGui.QPen(QtGui.QColor(*self.color), 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(*self.color), QtCore.Qt.SolidPattern))
            painter.drawEllipse(event.pos(), self.pen_size, self.pen_size)

            self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if 160 <= event.x() <= 120 + 601 and 60 <= event.y() <= 380:
            painter = QtGui.QPainter(self._im)
            painter.setPen(QtGui.QPen(QtGui.QColor(*self.color), 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(*self.color), QtCore.Qt.SolidPattern))
            painter.drawEllipse(event.pos(), self.pen_size, self.pen_size)
            self.update()
            pass

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self._im)

    def run(self):
        self.label.setText("OK")

    def white(self):
        self.color = (255, 255, 255)

    def black(self):
        self.color = (0, 0, 0)

    def change_size(self):
        self.pen_size = int(self.combo.currentText()) * 5

    def check(self):
        self.Answer.setText("Ваш Ответ Верен")
        if self.TextToSend.text() == self.mistery:
            self.Answer.setText("Ваш Ответ Верен")
        else:
            self.Answer.setText("Ваш Ответ Неверен")
        self.TextToSend.setText("")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
