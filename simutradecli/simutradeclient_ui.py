# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simutradeclient.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(620, 474)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.label.setObjectName("label")
        self.lineEditUrl = QtWidgets.QLineEdit(Dialog)
        self.lineEditUrl.setGeometry(QtCore.QRect(70, 8, 450, 20))
        self.lineEditUrl.setObjectName("lineEditUrl")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 76, 54, 12))
        self.label_2.setObjectName("label_2")
        self.lineEditSymbol = QtWidgets.QLineEdit(Dialog)
        self.lineEditSymbol.setGeometry(QtCore.QRect(70, 71, 91, 20))
        self.lineEditSymbol.setObjectName("lineEditSymbol")
        self.lineEditOrderQty = QtWidgets.QLineEdit(Dialog)
        self.lineEditOrderQty.setGeometry(QtCore.QRect(250, 70, 91, 20))
        self.lineEditOrderQty.setObjectName("lineEditOrderQty")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(190, 76, 54, 12))
        self.label_3.setObjectName("label_3")
        self.lineEditOrderPrice = QtWidgets.QLineEdit(Dialog)
        self.lineEditOrderPrice.setGeometry(QtCore.QRect(430, 69, 91, 20))
        self.lineEditOrderPrice.setObjectName("lineEditOrderPrice")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(370, 75, 54, 12))
        self.label_4.setObjectName("label_4")
        self.lineEditFilledPrice = QtWidgets.QLineEdit(Dialog)
        self.lineEditFilledPrice.setGeometry(QtCore.QRect(430, 96, 91, 20))
        self.lineEditFilledPrice.setObjectName("lineEditFilledPrice")
        self.lineEditFilledQty = QtWidgets.QLineEdit(Dialog)
        self.lineEditFilledQty.setGeometry(QtCore.QRect(250, 97, 91, 20))
        self.lineEditFilledQty.setObjectName("lineEditFilledQty")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(370, 102, 54, 12))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(190, 103, 54, 12))
        self.label_6.setObjectName("label_6")
        self.lineEditOrderNo = QtWidgets.QLineEdit(Dialog)
        self.lineEditOrderNo.setGeometry(QtCore.QRect(70, 99, 91, 20))
        self.lineEditOrderNo.setObjectName("lineEditOrderNo")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(10, 105, 54, 12))
        self.label_7.setObjectName("label_7")
        self.lineEditCorrId = QtWidgets.QLineEdit(Dialog)
        self.lineEditCorrId.setGeometry(QtCore.QRect(250, 123, 91, 20))
        self.lineEditCorrId.setObjectName("lineEditCorrId")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(190, 128, 54, 12))
        self.label_8.setObjectName("label_8")
        self.lineEditCorrType = QtWidgets.QLineEdit(Dialog)
        self.lineEditCorrType.setGeometry(QtCore.QRect(70, 125, 91, 20))
        self.lineEditCorrType.setObjectName("lineEditCorrType")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(10, 128, 54, 12))
        self.label_9.setObjectName("label_9")
        self.btnPushOrder = QtWidgets.QPushButton(Dialog)
        self.btnPushOrder.setGeometry(QtCore.QRect(530, 68, 81, 40))
        self.btnPushOrder.setObjectName("btnPushOrder")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(10, 167, 510, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.lineEditCostPrice = QtWidgets.QLineEdit(Dialog)
        self.lineEditCostPrice.setGeometry(QtCore.QRect(250, 183, 91, 20))
        self.lineEditCostPrice.setObjectName("lineEditCostPrice")
        self.lineEditCurrentQty = QtWidgets.QLineEdit(Dialog)
        self.lineEditCurrentQty.setGeometry(QtCore.QRect(70, 184, 91, 20))
        self.lineEditCurrentQty.setObjectName("lineEditCurrentQty")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(190, 189, 54, 12))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(10, 190, 54, 12))
        self.label_11.setObjectName("label_11")
        self.lineEditTradingDay = QtWidgets.QLineEdit(Dialog)
        self.lineEditTradingDay.setGeometry(QtCore.QRect(430, 32, 91, 20))
        self.lineEditTradingDay.setObjectName("lineEditTradingDay")
        self.lineEditAccountID = QtWidgets.QLineEdit(Dialog)
        self.lineEditAccountID.setGeometry(QtCore.QRect(250, 33, 91, 20))
        self.lineEditAccountID.setObjectName("lineEditAccountID")
        self.lineEditAccountType = QtWidgets.QLineEdit(Dialog)
        self.lineEditAccountType.setGeometry(QtCore.QRect(70, 34, 91, 20))
        self.lineEditAccountType.setObjectName("lineEditAccountType")
        self.label_12 = QtWidgets.QLabel(Dialog)
        self.label_12.setGeometry(QtCore.QRect(370, 38, 54, 12))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(Dialog)
        self.label_13.setGeometry(QtCore.QRect(10, 40, 54, 12))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(Dialog)
        self.label_14.setGeometry(QtCore.QRect(190, 39, 54, 12))
        self.label_14.setObjectName("label_14")
        self.lineEditLastPrice = QtWidgets.QLineEdit(Dialog)
        self.lineEditLastPrice.setGeometry(QtCore.QRect(430, 183, 91, 20))
        self.lineEditLastPrice.setObjectName("lineEditLastPrice")
        self.label_15 = QtWidgets.QLabel(Dialog)
        self.label_15.setGeometry(QtCore.QRect(370, 189, 54, 12))
        self.label_15.setObjectName("label_15")
        self.line_2 = QtWidgets.QFrame(Dialog)
        self.line_2.setGeometry(QtCore.QRect(10, 52, 510, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.btnPushPosition = QtWidgets.QPushButton(Dialog)
        self.btnPushPosition.setGeometry(QtCore.QRect(530, 179, 81, 51))
        self.btnPushPosition.setObjectName("btnPushPosition")
        self.lineEditCashAvail = QtWidgets.QLineEdit(Dialog)
        self.lineEditCashAvail.setGeometry(QtCore.QRect(250, 212, 91, 20))
        self.lineEditCashAvail.setObjectName("lineEditCashAvail")
        self.lineEditCash = QtWidgets.QLineEdit(Dialog)
        self.lineEditCash.setGeometry(QtCore.QRect(70, 213, 91, 20))
        self.lineEditCash.setObjectName("lineEditCash")
        self.label_16 = QtWidgets.QLabel(Dialog)
        self.label_16.setGeometry(QtCore.QRect(190, 218, 54, 12))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(Dialog)
        self.label_17.setGeometry(QtCore.QRect(10, 219, 54, 12))
        self.label_17.setObjectName("label_17")
        self.textEditLog = QtWidgets.QTextEdit(Dialog)
        self.textEditLog.setGeometry(QtCore.QRect(10, 250, 600, 220))
        self.textEditLog.setObjectName("textEditLog")
        self.lineEditSide = QtWidgets.QLineEdit(Dialog)
        self.lineEditSide.setGeometry(QtCore.QRect(430, 122, 91, 20))
        self.lineEditSide.setObjectName("lineEditSide")
        self.label_18 = QtWidgets.QLabel(Dialog)
        self.label_18.setGeometry(QtCore.QRect(370, 126, 54, 12))
        self.label_18.setObjectName("label_18")
        self.btnPushTrade = QtWidgets.QPushButton(Dialog)
        self.btnPushTrade.setGeometry(QtCore.QRect(530, 130, 81, 40))
        self.btnPushTrade.setObjectName("btnPushTrade")
        self.lineEditTradeNo = QtWidgets.QLineEdit(Dialog)
        self.lineEditTradeNo.setGeometry(QtCore.QRect(430, 148, 91, 20))
        self.lineEditTradeNo.setObjectName("lineEditTradeNo")
        self.label_19 = QtWidgets.QLabel(Dialog)
        self.label_19.setGeometry(QtCore.QRect(370, 153, 54, 12))
        self.label_19.setObjectName("label_19")
        self.lineEditOrderId = QtWidgets.QLineEdit(Dialog)
        self.lineEditOrderId.setGeometry(QtCore.QRect(250, 150, 91, 20))
        self.lineEditOrderId.setObjectName("lineEditOrderId")
        self.label_20 = QtWidgets.QLabel(Dialog)
        self.label_20.setGeometry(QtCore.QRect(190, 154, 54, 12))
        self.label_20.setObjectName("label_20")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "模拟交易端"))
        self.label.setText(_translate("Dialog", "服务地址"))
        self.label_2.setText(_translate("Dialog", "代码"))
        self.label_3.setText(_translate("Dialog", "委托数量"))
        self.label_4.setText(_translate("Dialog", "委托价格"))
        self.label_5.setText(_translate("Dialog", "成交价格"))
        self.label_6.setText(_translate("Dialog", "成交数量"))
        self.lineEditOrderNo.setToolTip(_translate("Dialog", "交易柜台的委托号EntruNo"))
        self.label_7.setText(_translate("Dialog", "委托号"))
        self.label_8.setText(_translate("Dialog", "关联号"))
        self.label_9.setText(_translate("Dialog", "关联类型"))
        self.btnPushOrder.setText(_translate("Dialog", "推送委托"))
        self.label_10.setText(_translate("Dialog", "持仓价格"))
        self.label_11.setText(_translate("Dialog", "持仓数量"))
        self.label_12.setText(_translate("Dialog", "交易日"))
        self.label_13.setText(_translate("Dialog", "账号类型"))
        self.label_14.setText(_translate("Dialog", "账号"))
        self.label_15.setText(_translate("Dialog", "最新价"))
        self.btnPushPosition.setText(_translate("Dialog", "推送持仓\n"
"(deprecated)"))
        self.label_16.setText(_translate("Dialog", "可用资金"))
        self.label_17.setText(_translate("Dialog", "账户资金"))
        self.label_18.setText(_translate("Dialog", "买卖方向"))
        self.btnPushTrade.setText(_translate("Dialog", "推送成交"))
        self.label_19.setText(_translate("Dialog", "成交编号"))
        self.lineEditOrderId.setToolTip(_translate("Dialog", "报单接口返回的订单号，类似于CATS算法单返回的算法单号"))
        self.label_20.setToolTip(_translate("Dialog", "报单接口返回的订单号，类似于CATS算法单返回的算法单号"))
        self.label_20.setText(_translate("Dialog", "订单号(新)"))

