import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.connection = sqlite3.connect('coffee.sqlite')
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
        res = self.connection.cursor().execute(query).fetchall()
        titles = ['ID', 'Название сорта', 'Степень обжарки', 'Молотый/В зернах',
                  'Описание вкуса', 'Цена', 'Объем упаковки']
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
