import sys

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QLabel, QLineEdit, QColorDialog, QDialog


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design.ui', self)
        self._im = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_ARGB32)
        self.color = "#000000" # цвет ручки

        self.clr.setStyleSheet("QPushButton {background-color: black; border-style: outset; border-width: 2px; "
                               "border-radius: 15px; border-color: black;padding: 4px;}") # стиль кнопки выбора цвета ручки
        self.pen_size = 1  # размер ручки
        self.size_text.setText('Размер ручки')

        self.mistery = "Дунаев"
        self.horizontalSlider.valueChanged.connect(self.change_size) # Слайдер для выбора размера ручки
        self.clr.clicked.connect(self.openColorDialog)
        self.Clear.clicked.connect(self.clear)
        self.l_x = -1   # условные координаты первой точки (значат, что ЛКМ отжата)
        self.l_y = -1   # условные координаты первой точки (значат, что ЛКМ отжата)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):              # Отрисовка точки, при отпускании ЛКМ мыши
        super().mouseReleaseEvent(event)
        if self.frame.geometry().x() <= event.x() <= self.frame.geometry().x() + self.frame.frameGeometry().width() and self.frame.geometry().y() <= event.y() <= self.frame.geometry().y() + self.frame.frameGeometry().height():
            painter = QtGui.QPainter(self._im)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.color), self.pen_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.SolidPattern))
            painter.drawEllipse(event.pos(), 1, 1)
            self.l_x = -1
            self.l_y = -1
            self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:         # Отрисовка линии на холсте, запоминаются координаты предедыдущей точки
                                                                        # и рисуется линия между настоящей точкой и предыдущей
                                                                        # Так работает отрисовка линии если ЛКМ зажата
        if self.frame.geometry().x() <= event.x() <= self.frame.geometry().x() + self.frame.frameGeometry().width() and self.frame.geometry().y() <= event.y() <= self.frame.geometry().y() + self.frame.frameGeometry().height():
            if self.l_x == -1 and self.l_y == -1:
                self.l_x = event.x() # координата точки в которой находится мышь
                self.l_y = event.y() # координата точки в которой находится мышь
            painter = QtGui.QPainter(self._im)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.color), self.pen_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.SolidPattern))
            painter.drawLine(self.l_x, self.l_y, event.x(), event.y()) # рисуем линию между предыдущей и текущей точкой
            self.l_x = event.x()  # запоминаем координаты точки
            self.l_y = event.y() # запоминаем координаты точки
            self.update()
            pass

    def paintEvent(self, event):        # отрисовка
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self._im)

    def change_size(self):              # изменение размера ручки
        self.pen_size = int(self.horizontalSlider.value())

    def openColorDialog(self):           # диалоговое окно для изменения цветаhttps://github.com/Cr0wley69/Crock/blob/main/main_game.py
        color = QColorDialog.getColor()

        if color.isValid():
            self.color = color.name()
            command = "QPushButton {background-color:" + self.color + "; border-style: outset; border-width: 2px; " \
                                                                      "border-radius: 15px; border-color: " \
                                                                      "black;padding: 4px;} "
            self.clr.setStyleSheet(command)

    def clear(self):                 # очистка поля для рисования
        rect = self.frame.frameRect()
        x = rect.getRect()[0] + self.frame.geometry().x()
        y = rect.getRect()[1] + self.frame.geometry().y()
        w = rect.getRect()[2]
        h = rect.getRect()[3]
        painter = QtGui.QPainter(self._im)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 0, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255), QtCore.Qt.SolidPattern))
        painter.drawRect(x, y, w, h)
        print(x, y, w, h)
        self.update()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

