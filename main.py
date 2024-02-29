import sys
import sqlite3

from release.mainForm import Ui_MainWindow
from release.addEditCoffeeForm import Ui_AddWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.add_btn.clicked.connect(self.add)
        self.edit_btn.clicked.connect(self.edit)

        self.con = sqlite3.connect('release/data/coffee.sqlite')
        self.load_table()

    def load_table(self):
        query = '''
                SELECT 
                    Coffees.id, 
                    Coffees.name,
                    RoastDegrees.roast_degree,
                    Types.type,
                    Coffees.flavor,
                    Coffees.price,
                    Coffees.volume
                FROM 
                    Coffees 
                INNER JOIN RoastDegrees ON RoastDegrees.id = Coffees.roast_degree
                INNER JOIN Types ON Types.id = Coffees.type'''
        res = self.con.cursor().execute(query).fetchall()
        titles = ['ID', 'Название сорта', 'Степень обжарки', 'Молотый/В зернах',
                  'Описание вкуса', 'Цена, руб.', 'Объем упаковки, см3']
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setHorizontalHeaderLabels(titles)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
                self.tableWidget.resizeColumnToContents(j)

    def add(self):
        self.add_widget = AddWidget(self)
        self.add_widget.show()

    def edit(self):
        try:
            items = self.tableWidget.selectedItems()
            if not items:
                self.statusBar().showMessage('Ничего не выбрано')
                return
            self.statusBar().clearMessage()
            rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            ids = [self.tableWidget.item(i, 0).text() for i in rows]
            for id_ in ids:
                self.edit_film_widget = AddWidget(self, id_)
                self.edit_film_widget.show()
        except Exception as r:
            print(r)


class AddWidget(QMainWindow, Ui_AddWindow):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.setupUi(self)

        self.con = sqlite3.connect('release/data/coffee.sqlite')
        self.roast_degrees = dict(self.con.cursor().execute('SELECT roast_degree, id FROM RoastDegrees').fetchall())
        self.types = dict(self.con.cursor().execute('SELECT type, id FROM Types').fetchall())
        self.roast_degree.addItems(self.roast_degrees.keys())
        self.type.addItems(self.types.keys())

        self.coffee_id = coffee_id
        if coffee_id is not None:
            self.pushButton.clicked.connect(self.edit_elem)
            self.pushButton.setText('Отредактировать')
            self.setWindowTitle('Редактирование записи')
            self.get_elem()
        else:
            self.pushButton.clicked.connect(self.add_elem)
            self.pushButton.setText('Добавить')
            self.setWindowTitle('Добавление записи')

    def get_verdict(self):
        return self.name.toPlainText() and self.flavor.toPlainText()

    def add_elem(self):
        if not self.get_verdict():
            self.statusBar().showMessage('Неверно заполненая форма')
            return
        self.statusBar().clearMessage()
        cur = self.con.cursor()
        cur.execute('INSERT INTO Coffees(name, roast_degree, type, flavor, price, volume) VALUES (?, ?, ?, ?, ?, ?)',
                    (self.name.toPlainText(), self.roast_degrees[self.roast_degree.currentText()],
                     self.types[self.type.currentText()], self.flavor.toPlainText(),
                     self.price.value(), self.volume.value()))
        self.con.commit()
        self.parent().load_table()
        self.close()

    def get_elem(self):
        query = '''
                SELECT 
                    Coffees.name,
                    RoastDegrees.roast_degree,
                    Types.type,
                    Coffees.flavor,
                    Coffees.price,
                    Coffees.volume
                FROM 
                    Coffees 
                INNER JOIN RoastDegrees ON RoastDegrees.id = Coffees.roast_degree
                INNER JOIN Types ON Types.id = Coffees.type
                WHERE Coffees.id = ?'''
        res = self.con.cursor().execute(query, self.coffee_id).fetchone()
        self.name.appendPlainText(str(res[0]))
        self.roast_degree.setCurrentText(str(res[1]))
        self.type.setCurrentText(str(res[2]))
        self.flavor.appendPlainText(str(res[3]))
        self.price.setValue(int(res[4]))
        self.volume.setValue(int(res[5]))

    def edit_elem(self):
        if not self.get_verdict():
            self.statusBar().showMessage('Неверно заполненая форма')
            return
        self.statusBar().clearMessage()
        cur = self.con.cursor()
        query = 'UPDATE Coffees SET name = ?, roast_degree = ?, type = ?, flavor = ?, price = ?, volume = ?'
        query += f'WHERE id = {self.coffee_id}'
        cur.execute(query,
                    (self.name.toPlainText(), self.roast_degrees[self.roast_degree.currentText()],
                     self.types[self.type.currentText()], self.flavor.toPlainText(),
                     self.price.value(), self.volume.value()))
        self.con.commit()
        self.parent().load_table()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
