import sys
from typing import List
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.domain.entity.complex import Complex


class DataEditView(QTableWidget):
    def __init__(self, data: List[Complex]):
        super().__init__()
        self.data = data
        self.setGeometry(800, 200, 300, 300)
        self.resize(290, 290)
        self.setRowCount(len([p for c in self.data for p in c.pyeongs]) + 1)
        self.setColumnCount(23)
        self.set_data()

    def set_data(self):
        row = 0
        self.setItem(row, 0, QTableWidgetItem("단지명"))
        self.setItem(row, 1, QTableWidgetItem("주소"))
        self.setItem(row, 2, QTableWidgetItem("동수"))
        self.setItem(row, 3, QTableWidgetItem("총세대수"))
        self.setItem(row, 4, QTableWidgetItem("입주년월일"))
        self.setItem(row, 5, QTableWidgetItem("최고층"))
        self.setItem(row, 6, QTableWidgetItem("구분"))
        self.setItem(row, 7, QTableWidgetItem("평형"))
        self.setItem(row, 8, QTableWidgetItem("전용면적"))
        self.setItem(row, 9, QTableWidgetItem("전용평형"))
        self.setItem(row, 10, QTableWidgetItem("공급면적"))
        self.setItem(row, 11, QTableWidgetItem("세대수"))
        self.setItem(row, 12, QTableWidgetItem("구조"))
        self.setItem(row, 13, QTableWidgetItem("방수"))
        self.setItem(row, 14, QTableWidgetItem("욕실수"))
        self.setItem(row, 15, QTableWidgetItem("최저매매가"))
        self.setItem(row, 16, QTableWidgetItem("매매거래일자"))
        self.setItem(row, 17, QTableWidgetItem("매매거래층"))
        self.setItem(row, 18, QTableWidgetItem("최고전세가"))
        self.setItem(row, 19, QTableWidgetItem("전세거래일자"))
        self.setItem(row, 20, QTableWidgetItem("전세거래층"))
        self.setItem(row, 21, QTableWidgetItem("전매제한여부"))
        self.setItem(row, 22, QTableWidgetItem("대표평형"))
        row = 1
        for c in self.data:
            for p in c.pyeongs:
                self.setItem(row, 0, QTableWidgetItem(str(c.complex_name)))
                self.setItem(row, 1, QTableWidgetItem(str(c.address)))
                self.setItem(row, 2, QTableWidgetItem(str(c.total_dong_count)))
                self.setItem(row, 3, QTableWidgetItem(str(c.total_household_count)))
                self.setItem(row, 4, QTableWidgetItem(str(c.completion_date)))
                self.setItem(row, 5, QTableWidgetItem(str(c.high_floor)))
                self.setItem(row, 6, QTableWidgetItem(str(c.type_name)))
                self.setItem(row, 7, QTableWidgetItem(str(p.pyeong_name)))
                self.setItem(row, 8, QTableWidgetItem(str(p.exclusive_area)))
                self.setItem(row, 9, QTableWidgetItem(str(p.exclusive_pyeong)))
                self.setItem(row, 10, QTableWidgetItem(str(p.supply_area)))
                self.setItem(row, 11, QTableWidgetItem(str(p.house_hold_count)))
                self.setItem(row, 12, QTableWidgetItem(str(p.entrance_type)))
                self.setItem(row, 13, QTableWidgetItem(str(str(p.room_count))))
                self.setItem(row, 14, QTableWidgetItem(str(p.bathroom_count)))
                self.setItem(row, 15, QTableWidgetItem(str(p.low_trade_price)))
                self.setItem(row, 16, QTableWidgetItem(str(p.trade_date)))
                self.setItem(row, 17, QTableWidgetItem(str(p.trade_floor)))
                self.setItem(row, 18, QTableWidgetItem(str(p.high_lease_price)))
                self.setItem(row, 19, QTableWidgetItem(str(p.lease_date)))
                self.setItem(row, 20, QTableWidgetItem(str(p.lease_floor)))
                self.setItem(row, 21, QTableWidgetItem("v" if p.is_restriction else ""))
                self.setItem(row, 22, QTableWidgetItem("v" if p.is_representative else ""))
                row += 1
