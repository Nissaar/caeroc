import sys
from caeroc import formulae
try:
    from PySide import QtCore
    from PySide.QtCore import Slot
    from PySide.QtGui import QDialog, QStandardItemModel, QApplication
    from caeroc.gui.base_pyside import Ui_CalcDialog
except ImportError:
    from PyQt5 import QtCore
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5.QtWidgets import QDialog, QStandardItemModel
    from caeroc.gui.base_pyqt import Ui_CalcDialog

class CalcDialog(QDialog):
    """
    Bridges all events in QApplication CalcApp to caeroc.formulae
    TODO: Error handling
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.ui = Ui_CalcDialog()
        self.ui.setupUi(self)
        # ----------Input------------
        self.key1 = self.ui.qcb1_input
        self.key2 = self.ui.qcb2_input
        self._default_values()
        # ---------Output------------
        self.table = self.ui.qtw_output
        self._setupModel()

    def _default_values(self):
        self.on_qrb1_isen_pressed()
        self.input1 = 1.0
        self.input2 = 0.0
        self.gamma = 1.4
        self.autocalc = False

    def _setupModel(self):
        self.model = QStandardItemModel(10, 2, self)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Parameter")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Value")

    @Slot()
    def on_qrb1_isen_pressed(self):
        self.mode = formulae.isentropic.Isentropic()
        self.key1_legend = {'M':'M','p/p0':'p_p0','rho/rho0':'rho_rho0',
                            'T/T0':'t_t0','A/A*(sub)':'A_At','A/A*(sup)':'A_At'}
        self.key2_legend = {'-':None}
        self.key1.addItems(self.key1_legend.keys())
        self.key2.addItems(self.key2_legend.keys())
        print 'MODE: '+self.mode.__doc__

    @Slot(float)
    def on_qdsb1_input_valueChanged(self, value):
        self.input1 = value
        if self.autocalc:
            self.on_qpb_calculate_released()

    @Slot(float)
    def on_qdsb2_input_valueChanged(self, value):
        self.input2 = value
        if self.autocalc:
            self.on_qpb_calculate_released()

    @Slot(float)
    def on_qdsb_gamma_valueChanged(self, value):
        self.gamma = value
        if self.autocalc:
            self.on_qpb_calculate_released()

    @Slot()
    def on_checkBox_stateChanged(self):
        self.autocalc = not self.autocalc
        print 'Auto calculate: ',self.autocalc

    @Slot()
    def on_qpb_calculate_released(self):
        key1 = self.key1_legend[self.key1.currentText()]
        key2 = self.key2_legend[self.key2.currentText()]
        if key2 is None:
            kwargs = {key1:self.input1, 'gamma':self.gamma}
        else:
            kwargs = {key1:self.input1, key2:self.input2, 'gamma':self.gamma}

        print kwargs
        self.mode.calculate(**kwargs)
        print self.mode.data
        
        # ------ Fill table --------------
        self.model.removeRows(0,
                              self.model.rowCount(QtCore.QModelIndex()),
                              QtCore.QModelIndex())
        row = 0
        for k in self.mode.keys:
            if self.mode.data[k]: #Not empty
                self.model.insertRows(row, 1, QtCore.QModelIndex())
                self.model.setData(self.model.index(row, 0, QtCore.QModelIndex()),
                                    k)
                self.model.setData(self.model.index(row, 1, QtCore.QModelIndex()),
                                    str(self.mode.data[k].pop()))
                row += 1

        self.table.setModel(self.model)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = CalcDialog()
    calculator.show()
    sys.exit(app.exec_())
