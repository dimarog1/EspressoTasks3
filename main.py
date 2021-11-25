import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.update_result)
        self.pushButton_3.clicked.connect(self.insert_item)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.modified = {}
        self.titles = None
        self.max_id = 1

    def update_result(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute("SELECT * FROM coffee WHERE " + self.textEdit.toPlainText()).fetchall()
        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))
        # Если запись не нашлась, то не будем ничего делать
        if not result:
            return
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()
        self.save_results(int(self.tableWidget.item(item.row(), 0).text()))
        if int(self.tableWidget.item(item.row(), 0).text()) > self.max_id:
            self.max_id = int(self.tableWidget.item(item.row(), 0).text())

    def save_results(self, id):
        try:
            if self.modified:
                cur = self.con.cursor()
                que = "UPDATE coffee SET\n"
                que += ", ".join([f"{key}='{self.modified.get(key)}'"
                                  for key in self.modified.keys()])
                que += f" WHERE id = {id}"
                cur.execute(que)
                self.con.commit()
                self.modified.clear()
        except Exception as e:
            print(e)
            exit()

    def insert_item(self):
        try:
            ui = Edit(self)
            ui.exec_()
        except Exception as e:
            print(e)


class Edit(QDialog):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.addButton.clicked.connect(self.add)
        self.parent = parent

    def add(self):
        cur = self.con.cursor()
        try:
            que = f"INSERT INTO coffee(id,name,sort,roast_degree,type,flavour_description,price,packing_volume) VALUES ({self.parent.max_id + 1}, '{self.name.text()}', '{self.sort.text()}', '{self.roast_degree.text()}'," \
                  f" '{self.type.text()}', '{self.flavour_description.text()}', {self.price.text()}, {self.packing_volume.text()})"
            print(que)
            cur.execute(que)
            self.accepted.setText('Добавлено!')
            self.con.commit()
            self.parent.max_id += 1
        except Exception as e:
            print(e)
            exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
