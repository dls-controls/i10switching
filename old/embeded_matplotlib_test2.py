#!/bin/env dls-python

import dls_packages

from pylab import *
import sys
from PyQt4 import QtGui, QtCore, uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt4.uic import loadUiType

import random


 	
Ui_MainWindow, QMainWindow = loadUiType('i10chicgui.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.plotLayout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(10)]
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.plot(data, '*-')
        self.canvas.draw()

 
if __name__ == '__main__':
 
    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())

