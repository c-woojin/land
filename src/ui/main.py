import sys
import time
from typing import List, Tuple
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QPushButton,
    QProgressDialog, QMessageBox, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt

from src.services import service, data_handler
from src.domain.entity.complex import Complex
from src.domain.values import Region
from src.ui.data_edit import DataEditView


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.is_progress_canceled = False
        self.cities = []
        self.regions = []
        self.towns = []
        self.cb_city = QComboBox()
        self.cb_region = QComboBox()
        self.cb_town = QComboBox()
        self.btn_import = QPushButton('데이터수집')
        self.data: List[Tuple[Region, List[Complex]]] = []
        self.data_list_widget = QListWidget()
        self.btn_data_remove = QPushButton('선택삭제')
        self.btn_data_edit = QPushButton('자세히')
        self.btn_data_excel = QPushButton('엑셀출력(평형데이터)')
        self.btn_data_analysis_excel = QPushButton('엑셀출력(동별가격비교)')
        self.main_box = QVBoxLayout()
        self.init_handler()
        self.init_ui()

    def init_ui(self):
        self.main_box = QVBoxLayout()
        self.set_default_box()
        self.setWindowTitle('QComboBox')
        self.setGeometry(300, 300, 300, 200)
        self.show()
        self.cities = service.get_main_cities()
        self.cb_city.clear()
        self.cb_city.addItem('선택')
        for city in self.cities:
            self.cb_city.addItem(city.region_name)

    def set_default_box(self):
        lbl_city = QLabel('시/도')
        self.cb_city.addItem('초기화중')

        lbl_region = QLabel('시/군/구')
        lbl_town = QLabel('읍/면/동')

        region_select_box = QHBoxLayout()
        region_select_box.addStretch(1)
        region_select_box.addWidget(lbl_city)
        region_select_box.addWidget(self.cb_city)
        region_select_box.addWidget(lbl_region)
        region_select_box.addWidget(self.cb_region)
        region_select_box.addWidget(lbl_town)
        region_select_box.addWidget(self.cb_town)
        region_select_box.addStretch(1)

        btn_box = QHBoxLayout()
        btn_box.addWidget(self.btn_import)

        data_list_box = QHBoxLayout()
        data_list_box.addWidget(self.data_list_widget)
        data_list_btn_box = QVBoxLayout()
        data_list_btn_box.addWidget(self.btn_data_remove)
        data_list_btn_box.addWidget(self.btn_data_edit)
        data_list_btn_box.addWidget(self.btn_data_excel)
        data_list_btn_box.addWidget(self.btn_data_analysis_excel)
        data_list_box.addLayout(data_list_btn_box)

        self.main_box.addLayout(region_select_box)
        self.main_box.addLayout(btn_box)
        self.main_box.addLayout(data_list_box)
        self.setLayout(self.main_box)

    def init_handler(self):
        self.cb_city.activated.connect(self.city_selected)
        self.cb_region.activated.connect(self.region_selected)
        self.btn_import.clicked.connect(self.start_import)
        self.btn_data_remove.clicked.connect(self.data_remove_pushed)
        self.btn_data_edit.clicked.connect(self.data_edit_pushed)
        self.btn_data_excel.clicked.connect(self.data_excel_pushed)
        self.btn_data_analysis_excel.clicked.connect(self.data_analysis_excel_pushed)

    def city_selected(self):
        city_index = self.cb_city.currentIndex()
        if city_index == 0:
            self.cb_region.clear()
            self.cb_town.clear()
            return
        region_no = self.cities[city_index-1].region_no
        self.regions = service.get_regions(region_no)
        self.cb_region.clear()
        self.cb_town.clear()
        self.cb_region.addItem('선택')
        for region in self.regions:
            self.cb_region.addItem(region.region_name)

    def region_selected(self):
        region_index = self.cb_region.currentIndex()
        if region_index == 0:
            self.cb_town.clear()
            return
        region_no = self.regions[region_index-1].region_no
        self.towns = service.get_regions(region_no)
        self.cb_town.clear()
        self.cb_town.addItem('선택')
        for town in self.towns:
            self.cb_town.addItem(town.region_name)

    def data_remove_pushed(self):
        if self.data:
            row = self.data_list_widget.currentRow()
            self.data_list_widget.takeItem(row)
            self.data.pop(row)

    def data_edit_pushed(self):
        if self.data:
            row = self.data_list_widget.currentRow()
            print(self.data[row][1])
            self.data_edit_view = DataEditView(data=self.data[row][1])
            self.data_edit_view.show()

    def data_excel_pushed(self):
        file_name, ok = QFileDialog.getSaveFileUrl(self, "저장할 위치를 선택하세요.")
        if ok:
            data_handler.LandXlsHandler(file_name.path() + ".xlsx", self.data).write_raw_xls()
            QMessageBox.information(self, "성공", "엑셀추출이 완료되었습니다.", QMessageBox.Ok)

    def data_analysis_excel_pushed(self):
        file_name, ok = QFileDialog.getSaveFileUrl(self, "저장할 위치를 선택하세요.")
        if ok:
            data_handler.LandXlsHandler(file_name.path() + ".xlsx", self.data).write_analysis_xls(2010, 2000)
            QMessageBox.information(self, "성공", "엑셀추출이 완료되었습니다.", QMessageBox.Ok)

    def start_import(self):
        town_index = self.cb_town.currentIndex()
        if town_index == -1 or town_index == 0:
            return
        town = self.towns[town_index-1]
        wait_pop = QMessageBox(text="잠시만 기다려 주세요", parent=self)
        wait_pop.setWindowModality(Qt.WindowModal)
        wait_pop.show()
        complexes = service.get_complexes(town.region_no)
        progress_title = f'{self.cb_city.currentText()} {self.cb_region.currentText()} {self.cb_town.currentText()} {len(complexes)}개 단지의 데이터를 수집합니다.'
        wait_pop.close()
        progress_dialog = QProgressDialog(progress_title, "취소", 0, len(complexes)+1, self) if complexes else QProgressDialog("수집할 데이터가 없습니다.", "취소", 0, len(complexes)+1, self)
        progress_dialog.canceled.connect(self.progress_canceled)
        progress = 0
        progress_dialog.setValue(progress)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        for complex in complexes:
            if self.is_progress_canceled is True:
                self.is_progress_canceled = False
                break
            time.sleep(0.3)
            progress_text = f'[{progress}/{len(complexes)}] {complex.complex_name} 단지 데이터를 수집중입니다.'
            progress_dialog.setLabelText(progress_text)
            service.apply_price(complex)
            progress += 1
            progress_dialog.setValue(progress)
        progress += 1
        progress_dialog.setValue(progress)
        if complexes:
            self.append_data((town, complexes))

    def progress_canceled(self):
        self.is_progress_canceled = True

    def append_data(self, data: Tuple[Region, List[Complex]]):
        self.data.append(data)
        item = QListWidgetItem(data[0].region_name)
        self.data_list_widget.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
