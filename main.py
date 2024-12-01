import sys
from PyQt6 import uic
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget


class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Эспрессо')
        uic.loadUi('main.ui', self)
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT roasting_degree FROM coffee""")
        mn = set()
        self.choose_st_ob.addItem('Любая')
        self.choose_type.addItem('Любой')
        self.choose_type.addItem('Молотый')
        self.choose_type.addItem('Зерновой')
        for elem in data:
            mn.add(elem[0])
        con.close()
        for elem in mn:
            self.choose_st_ob.addItem(elem)
        self.search_button.clicked.connect(self.run)
        self.admin_button.clicked.connect(self.open_second_form)
    
    def run(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        sp_cond = []
        zapros = "SELECT * FROM coffee"
        if self.name_input.text() != '':
            sp_cond.append(f"name LIKE '%{self.name_input.text()}%'")
        if self.choose_st_ob.currentText() != 'Любая':
            sp_cond.append(f'roasting_degree = "{self.choose_st_ob.currentText()}"')
        if self.choose_type.currentText() != 'Любой':
            sp_cond.append(f'ground_or_grain = "{self.choose_type.currentText()}"')
        if len(sp_cond) > 0:
            zapros += ' WHERE '
            out = ' AND '.join(sp_cond)
            zapros += out
        res = cur.execute(zapros)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки',
                                                    'Молотый / в зёрнах', 'Описание вкуса',
                                                    'Цена, руб', 'Объём упаковки'])
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()
    
    def open_second_form(self):
        self.second_form = SecondForm()
        self.second_form.show()


class SecondForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Изменение БД')
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.type_edit.addItem('Молотый')
        self.type_edit.addItem('Зерновой')
        self.pushButton.clicked.connect(self.run)
    
    def run(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT name FROM coffee""")
        mn = set()
        for elem in data:
            mn.add(elem[0])
        if self.name_edit.text() in mn:
            cur.execute(f'''UPDATE coffee
                        SET roasting_degree = '{self.st_edit.text()}',
                        ground_or_grain = '{self.type_edit.currentText()}',
                        taste_description = '{self.textEdit.toPlainText()}',
                        price = '{self.cost_edit.text()}',
                        volume = '{self.volume_edit.text()}'
                        WHERE name = "{self.name_edit.text()}"''')
        else:
            cur.execute(f'''INSERT INTO coffee(name, roasting_degree, ground_or_grain, 
                        taste_description, price, volume) VALUES("{self.name_edit.text()}",
                        "{self.st_edit.text()}", "{self.type_edit.currentText()}",
                        "{self.textEdit.toPlainText()}", "{self.cost_edit.text()}",     
                        "{self.volume_edit.text()}")''')
        con.commit()
        con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    ex.show()
    sys.exit(app.exec())