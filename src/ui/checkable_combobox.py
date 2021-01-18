from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# new check-able combo box
class CheckableComboBox(QComboBox):

    # constructor
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.selected = set()

    count = 0

    # action called when item get checked
    def do_action(self):
        pass
        # when any item get pressed

    def handleItemPressed(self, index):

        # getting the item
        item = self.model().itemFromIndex(index)

        # checking if item is checked
        if item.checkState() == Qt.Checked:

            # making it unchecked
            item.setCheckState(Qt.Unchecked)
            self.selected.remove(index.row())
            # if not checked
        else:
            # making the item checked
            item.setCheckState(Qt.Checked)
            self.selected.add(index.row())

    def get_select_items(self):
        return self.selected