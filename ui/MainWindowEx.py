import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QColor
from ui.MainWindow import Ui_MainWindow
from models.user.tabAccount.EditDateEx import EditDateEx

class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self, user_email=None):
        super().__init__()
        self.setupUi(self)
        self.current_user_email = user_email
        self.selected_row = None
        self.current_user_bookings = []
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
        self.json_path = os.path.join(PROJECT_ROOT, "datasets", "bookings.json")
        self.setupSignalAndSlot()
        self.tabWidget.setCurrentIndex(0)

    def setupSignalAndSlot(self):
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.tableWidget.cellClicked.connect(self.show_booking_detail)
        if hasattr(self, "pushButtonChange"):
            self.pushButtonChange.clicked.connect(self.open_edit_window)
        if hasattr(self, "pushButtonDelete"):
            self.pushButtonDelete.clicked.connect(self.delete_booking)

    def on_tab_changed(self, index):
        if self.tabWidget.tabText(index) == "Chỉnh lịch":
            self.load_user_bookings()

    def load_user_bookings(self):
        if not self.current_user_email:
            return
        if not os.path.exists(self.json_path):
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
        except:
            return
        user_bookings = []
        for b in bookings:
            if b.get("email", "").strip().lower() == self.current_user_email.strip().lower():
                user_bookings.append(b)
        self.current_user_bookings = user_bookings
        self.display_bookings(user_bookings)

    def display_bookings(self, bookings):
        self.tableWidget.setRowCount(0)
        now = datetime.now()
        for row_idx, b in enumerate(bookings):
            self.tableWidget.insertRow(row_idx)
            concept_item = QTableWidgetItem(b.get("concept", ""))
            time_item = QTableWidgetItem(b.get("time", ""))
            date_item = QTableWidgetItem(b.get("date", ""))
            place_item = QTableWidgetItem(b.get("place", ""))
            self.tableWidget.setItem(row_idx, 0, concept_item)
            self.tableWidget.setItem(row_idx, 1, time_item)
            self.tableWidget.setItem(row_idx, 2, date_item)
            self.tableWidget.setItem(row_idx, 3, place_item)
            try:
                booking_time = datetime.strptime(
                    b.get("date") + " " + b.get("time"),
                    "%d/%m/%Y %H:%M"
                )
                if booking_time < now:
                    color = QColor(255, 200, 200)
                else:
                    color = QColor(200, 255, 200)
                for col in range(4):
                    item = self.tableWidget.item(row_idx, col)
                    if item:
                        item.setBackground(color)
            except:
                pass

    def show_booking_detail(self, row, column):
        if row >= len(self.current_user_bookings):
            return
        self.selected_row = row
        data = self.current_user_bookings[row]
        self.lineEditName_2.setText(data.get("name", ""))
        self.lineEditPhone_2.setText(data.get("phone", ""))
        self.lineEditEmail_2.setText(data.get("email", ""))
        self.lineEditConcept.setText(data.get("concept", ""))
        self.lineEditBackground.setText(data.get("background", ""))
        thoi_diem = data.get("date", "") + " - " + data.get("time", "")
        self.lineEditTime.setText(thoi_diem)
        dia_diem = data.get("place", "")
        if data.get("place_detail", "") != "":
            dia_diem += " - " + data.get("place_detail", "")
        self.lineEditPlace.setText(dia_diem)
        self.textEditNote.setPlainText(data.get("note", ""))

    def open_edit_window(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn lịch cần chỉnh")
            return
        data = self.current_user_bookings[self.selected_row]
        self.edit_window = QMainWindow()
        self.edit_ui = EditDateEx()
        self.edit_ui.setupUi(self.edit_window)
        self.edit_ui.load_data(data)
        self.edit_ui.refresh_callback = self.load_user_bookings
        self.edit_window.show()

    def delete_booking(self):
        row = self.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn lịch cần xóa")
            return
        data = self.current_user_bookings[row]
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa lịch này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not os.path.exists(self.json_path):
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
        except:
            return
        new_bookings = []
        for b in bookings:
            if not (
                b.get("email") == data.get("email") and
                b.get("date") == data.get("date") and
                b.get("time") == data.get("time")
            ):
                new_bookings.append(b)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(new_bookings, f, ensure_ascii=False, indent=4)
        except:
            QMessageBox.critical(self, "Lỗi", "Không thể ghi file JSON")
            return
        QMessageBox.information(self, "Thành công", "Đã xóa lịch")
        self.load_user_bookings()

