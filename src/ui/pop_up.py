from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import Qt

class PopUp(QMessageBox):
    def __init__(self, message: str, parent: QWidget):
        super().__init__()
        self.setParent(parent)
        self.setGeometry(800, 200, 300, 300)
        self.resize(290, 290)
        self.setText(message)
        self.setWindowModality(Qt.WindowModal)
