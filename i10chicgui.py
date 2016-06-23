

import dls_packages
import sys
from PyQt4 import QtGui, QtCore

class Control(QtGui.QMainWindow):

    def __init__(self):
        super(Control, self).__init__()
        self.initUI()

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        btn = QtGui.QPushButton("Plot",self)
        btn.clicked.connect(self.plotgraphs)
        # this will eventually make the animation happen!
        # then add extra buttons to adjust things


        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('i10chic GUI')    
        self.resize(250, 150)
        self.show()

    def plotgraphs(self):
        return Create_plots().show_plot()



def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Control()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
