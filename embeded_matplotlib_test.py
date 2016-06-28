#!/bin/env dls-python

import dls_packages

import cothread
from cothread.catools import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pylab import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import random


class MyTestCanvas(FigureCanvas):
    pass


class TestWindow(QDialog):

    def __init__ (self):
        super(TestWindow, self).__init__()
        self.setWindowTitle("Test Window")

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)

        self.plot()

    def plot(self):
        data = [random.random() for i in range(10)]
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.plot(data, '*-')
        self.canvas.draw()


def main():
    cothread.iqt()
    test_window = TestWindow()
    test_window.show()
    cothread.WaitForQuit()
    sys.exit()

if __name__ == '__main__':
    main()
