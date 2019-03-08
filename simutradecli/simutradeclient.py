# encoding: UTF-8
#
# Copyright 2018 BigQuant, Inc.
#
# 模拟交易数据模拟端
#

import logging
import json
import requests
import sys
import time
from datetime import datetime, timedelta

from PyQt5.QtCore import pyqtSignal
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon, QFont
from qtpy.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QStatusBar

from simutradeclient_ui import Ui_Dialog


headers = {'content-type': "application/json", 'Authorization': 'APP appid = 4abf1a,token = 9480295ab2e2eddb8'}

def post_data(url, addr, data):
    """请求获取资源信息"""
    if addr[0] == "/":
        _url = url + addr
    else:
        _url = url + "/" + addr

    token = "YmlncXVhbnRiaWdxdWFudA=="
    body = {'token': token, **data}
    data = json.dumps(body)

    ret = requests.post(_url, data=data, headers=headers, timeout=5)
    return json.loads(ret.text)


class StdOutput(object):
    def __init__(self, parent, flag, out2std=True):
        self.parent = parent
        self.flag = flag
        self.terminal = sys.stdout if out2std else None

    def write(self, message):
        if message == '\n':
            return

        if self.terminal is not None:
            self.terminal.write(message)
        self.parent.ui_log(message, self.flag)

    def flush(self):
        pass

class SimuTradeClientWindow(QMainWindow, Ui_Dialog):
    _signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(SimuTradeClientWindow, self).__init__(parent)
        self.setupUi(self)

        sys.stdout = StdOutput(self, flag=True)

        self.btnPushOrder.clicked.connect(self.slot_push_order)
        self.btnPushPosition.clicked.connect(self.slot_push_position)

        self.setting = {}
        self.read_and_init_config()

    def read_and_init_config(self):
        filename = "simutradeclient.json"
        try:
            with open(filename, 'r') as fp:
                self.setting = json.load(fp)
        except FileNotFoundError:
            pass

        # set some default values
        cats_receiver = self.setting.get("cats_receiver",\
                                         "http://127.0.0.1:6001")
        accountType = self.setting.get("accountType", "S0")
        accountID = self.setting.get("accountID", "701145001")
        tradingDay = self.setting.get("tradingDay")
        self.lineEditUrl.setText(cats_receiver)
        self.lineEditAccountType.setText(accountType)
        self.lineEditAccountID.setText(accountID)
        if not tradingDay:
            tradingDay = datetime.now().strftime("%Y-%m-%d")
        self.lineEditTradingDay.setText(tradingDay)

        def set_default_value(lineEdit, keyName):
            value = self.setting.get(keyName)
            if value:
                lineEdit.setText(str(value))

        # 若配置了则设置默认值
        set_default_value(self.lineEditSymbol, "symbol")
        set_default_value(self.lineEditOrderQty, "orderQty")
        set_default_value(self.lineEditOrderPrice, "orderPrice")
        set_default_value(self.lineEditFilledQty, "filledQty")
        set_default_value(self.lineEditFilledPrice, "filledPrice")
        set_default_value(self.lineEditOrderNo, "orderNo")
        set_default_value(self.lineEditSide, "side")
        set_default_value(self.lineEditSide, "tradeSide")
        set_default_value(self.lineEditCorrType, "corrType")
        set_default_value(self.lineEditCorrId, "corrID")

        set_default_value(self.lineEditCurrentQty, "currentQty")
        set_default_value(self.lineEditCostPrice, "costPrice")
        set_default_value(self.lineEditLastPrice, "lastPrice")
        set_default_value(self.lineEditCash, "cash")
        set_default_value(self.lineEditCashAvail, "cashAvail")

    def slot_push_order(self):
        """推送订单数据"""
        accttype = self.lineEditAccountType.text()
        account = self.lineEditAccountID.text()
        if not accttype or not account:
            self.ui_log("push_order invalid account data!")
            return

        try:
            symbol = self.lineEditSymbol.text()
            orderQty = int(self.lineEditOrderQty.text())
            orderPrice = float(self.lineEditOrderPrice.text())
            tradeSide = self.lineEditSide.text()
            filledQty = int(self.lineEditFilledQty.text())
            avgPrice = float(self.lineEditFilledPrice.text())
            corrType = self.lineEditCorrType.text()
            corrId = self.lineEditCorrId.text()
            run_date = self.lineEditTradingDay.text()
            orderNo = self.lineEditOrderNo.text()
            orderTime = datetime.now().strftime("%H%M%S")
            orderStatus = 1 # 部分成交
            orderType = "U"
        except Exception as err:
            self.ui_log("push_order invalid data, err:%s!" % (err))
            return

        data = {
            'trade_accttype': accttype,
            'trade_acct': account,
            'orderDetail': [
                { 'symbol': symbol, 'orderQty': orderQty, 'orderPrice': orderPrice, 'tradeSide': tradeSide,
                  'orderType': orderType, 'orderParam': '', 'orderNo': orderNo, 'filledQty': filledQty,
                  'avgPrice': avgPrice, 'cancelQty': 0, 'orderTime': orderTime, 'status': orderStatus,
                  'corrType': corrType, 'corrId': corrId, 'run_date': run_date }
            ]
        }
        order_data = {'order_data': data}

        url = self.lineEditUrl.text()
        try:
            post_data(url, "/order", order_data)
        except Exception as err:
            self.ui_log("push_order exception:%s!" % (err))
            return

        # 输入日志
        side_desc = "买" if tradeSide == '1' else "卖"
        if filledQty > 0:
            msg = "%s%s %d@%.2f 成交%d@%.2f 委托号%s" % (side_desc, symbol, orderQty, orderPrice, filledQty, avgPrice, orderNo)
        else:
            msg = "%s%s %d@%.2f 委托号%s" % (side_desc, symbol, orderQty, orderPrice, orderNo)
        self.ui_log(msg)

    def slot_push_position(self):
        """持仓推送"""
        accttype = self.lineEditAccountType.text()
        account = self.lineEditAccountID.text()
        if not accttype or not account:
            self.ui_log("push_order invalid account data!")
            return

        try:
            symbol = self.lineEditSymbol.text()
            currentQty = int(self.lineEditCurrentQty.text())
            costPrice = float(self.lineEditCostPrice.text())
            lastPrice = float(self.lineEditLastPrice.text())
            cash = float(self.lineEditCash.text())
            cashAvail = float(self.lineEditCashAvail.text())
            run_date = self.lineEditTradingDay.text()
        except Exception as err:
            self.ui_log("push_position invalid data, err:%s!" % (err))
            return

        data = {
            'trade_accttype': accttype,
            'trade_acct': account,
            'currentBalance': cash,
            'enabledBalance': cashAvail,
            'posDetail': [
                { 'symbol': symbol, 'securityName': symbol[:6], 'currentQty': currentQty, 'enabledQty': currentQty,
                  'costPrice': costPrice, 'lastPrice': lastPrice, 'marketValue': currentQty * lastPrice,
                  'run_date': run_date }
            ]
        }
        position_data = {'position': data}

        url = self.lineEditUrl.text()
        try:
            post_data(url, "/position", position_data)
        except Exception as err:
            self.ui_log("push_position exception:%s!" % (err))
            return

        # 输入日志
        msg = "%s持仓%d@%.2f 最新价%.2f" % (symbol, currentQty, costPrice, lastPrice)
        self.ui_log(msg)

    def closeEvent(self, event):
        """关闭事件"""
        rv = QMessageBox.question(self, "退出", "确定退出?",
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
        if rv == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def ui_log(self, msg, printTime=True, callQtEvents=False):
        """显示log信息在界面上"""
        if printTime:
            t = datetime.now()
            logMsg = t.strftime('%H:%M:%S ') + msg
        else:
            logMsg = msg

        self.textEditLog.append(logMsg)
        if callQtEvents:
            QApplication.processEvents()


# ----------------------------------------------------------------------
if __name__ == '__main__':
    qApp = QApplication([])
    mw = SimuTradeClientWindow()
    mw.show()

    qApp.exec_()
