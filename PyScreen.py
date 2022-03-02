import sys, datetime, pyperclip, win32clipboard, pytesseract, keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab, Image
from io import BytesIO


class SnippingWidget(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 2

        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        try:
            r = QtCore.QRect(self.start_point, self.end_point).normalized()
            self.hide()
            img = ImageGrab.grab(bbox=r.getCoords())
            
            self.filepath = "screenshots/" + datetime.datetime.today().strftime("%H%M%S") + ".png"
            img.save(self.filepath)
        except:
            print("Пуста картинка")

        def send_to_clipboard(clip_type, data):
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(clip_type, data)
            win32clipboard.CloseClipboard()
        try:
            image = Image.open(self.filepath)

            output = BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            send_to_clipboard(win32clipboard.CF_DIB, data)
        except:
            print("Пуста картинка")
            
        QtWidgets.QApplication.restoreOverrideCursor()
        self.closed.emit()
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

    def paintEvent(self, event):
        trans = QtGui.QColor(22, 100, 233)
        r = QtCore.QRectF(self.start_point, self.end_point).normalized()
        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        self.snipper = SnippingWidget()
        self.snipper.showFullScreen()
        self.snipper.closed.connect(self.on_closed)
       
    def on_closed(self):
        self.filepath = "screenshots/" + datetime.datetime.today().strftime("%H%M%S") + ".png"

        try:
            self.img = Image.open(self.filepath)


            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            self.custom_config = r' --oem 1 --psm 6'

            self.text = pytesseract.image_to_string(self.img, lang='eng+rus+ukr', config = self.custom_config)
            pyperclip.copy(self.text)

            keyboard.wait("Alt + shift + q")

            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
            self.snipper = SnippingWidget()
            self.snipper.showFullScreen()
            self.snipper.closed.connect(self.on_closed)
        except:
            keyboard.wait("Alt + shift + q")

            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
            self.snipper = SnippingWidget()
            self.snipper.showFullScreen()
            self.snipper.closed.connect(self.on_closed)


if __name__ == "__main__":
    keyboard.wait("Alt + shift + q")
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())

