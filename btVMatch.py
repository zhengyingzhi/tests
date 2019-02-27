# encoding: UTF-8
#
# Copyright 2018 BigQuant, Inc.
#
# 模拟撮合模型
#

import math
from copy import copy
from datetime import datetime
from queue import Queue, Empty
from threading import Thread

from bigtrader.btConstant import *
from bigtrader.btObject import BtOrderReq, BtCancelOrderReq
from bigtrader.btObject import BtBarData, BtTickData, BtOrderData, BtTradeData

EV_REQ_ORDER = 'eReqOrder'
EV_REQ_CANCEL = 'eReqCancel'

########################################################################
class TradeInfo:
    """成交信息"""
    def __init__(self, order, trade_id, trade_volume, trade_price, trade_date, trade_time):
        """成交信息"""
        self.order = order
        self.traded_order = copy(order)
        self.trade_id = trade_id
        self.trade_volume = trade_volume
        self.trade_price = trade_price
        self.trade_date = trade_date
        self.trade_time = trade_time
        # self.trade_money = trade_volume * trade_price

    def __repr__(self):
        return "TradeInfo(trade_id:{},trade_volume:{},trade_price:{},trade_time:{} {})"\
               .format(self.trade_id, self.trade_volume, self.trade_price, self.trade_date, self.trade_time)

class SimPosition(object):
    """简单持仓"""
    def __init__(self, multiplier, is_future):
        self.multiplier = multiplier
        assert multiplier > 0, "multiplier should be > 0"
        if is_future:
            self.update_position = self.update_future_position
        else:
            self.update_position = self.update_equity_position

        self.long_share = 0         # 多仓
        self.long_price = 0.0       # 多仓价格
        self.long_frozen = 0        # 多仓冻结
        self.long_value = 0.0       # 多仓价值
        self.short_share = 0        # 空仓
        self.short_price = 0.0
        self.short_frozen = 0
        self.short_value = 0

        self.closed_pnl = 0.0       # 平仓盈亏
        self.last_price = 0.0       # 最新价

    def __repr__(self):
        return "SimPosition(long:{},{},{} | short:{},{},{} | lastpx:{}, rpnl:{})"\
               .format(self.long_share, self.long_price, self.long_frozen, 
                       self.short_share, self.short_price, self.short_frozen,
                       self.last_price, self.closed_pnl)

    @property
    def long_avail(self):
        return self.long_share - self.long_frozen

    @property
    def short_avail(self):
        return self.short_share - self.short_frozen

    def update_long_frozen(self, frozen_share):
        """更新多头冻结数量"""
        self.long_frozen += frozen_share

    def update_short_frozen(self, frozen_share):
        """更新空头冻结数量"""
        self.short_frozen += frozen_share

    def update_future_position(self, trade):
        """更新期货持仓"""
        if trade.offset == OFFSET_OPEN:
            if trade.direction == DIRECTION_LONG:
                self.long_value += trade.volume * trade.price
                self.long_share += trade.volume
                self.long_price = self.long_value / self.long_share
            else:
                self.short_value += trade.volume * trade.price
                self.short_share += trade.volume
                self.short_price = self.short_value / self.short_share
        else:
            if trade.direction == DIRECTION_LONG:
                self.closed_pnl += (self.short_price - trade.price) * trade.volume * self.multiplier
                self.short_share -= trade.volume
                self.short_share = self.short_share * self.short_price
                self.update_short_frozen(-trade.volume)
            else:
                self.closed_pnl += (trade.price - self.long_price) * trade.volume * self.multiplier
                self.long_share -= trade.volume
                self.long_share = self.long_share * self.long_price
                self.update_long_frozen(-trade.volume)

    def update_equity_position(self, trade):
        """更新股票持仓"""
        if trade.direction == DIRECTION_LONG:
            self.long_value += trade.volume * trade.price
            self.long_share += trade.volume
            self.long_price = self.long_value / self.long_share
        else:
            self.closed_pnl += (trade.price - self.long_price) * trade.volume
            self.long_share -= trade.volume
            self.long_share = self.long_share * self.long_price
            self.update_long_frozen(-trade.volume)


"""
实时行情：
1. 行情线程收到行情后，put到工作线程中
2. 工作线程根据新行情，扫描挂单，进行撮合，并记录最新一笔tick行情
3. 得到撮合结果，生成订单变化通知，成交通知等
4. 允许开仓，但有限平仓
"""

class VMatchEngine(object):
    """撮合引擎，只负责订单的撮合"""
    # 成交编号
    trade_id = 0

    PRICETYPE_TOBE_CANCELED = set([PRICETYPE_MARKETPRICE, PRICETYPE_FAK, PRICETYPE_FOK])

    def __init__(self):
        """只负责撮合"""
        self.last_mds = {}          # 上一次行情

        self.price_impact = 0.1
        self.volume_limit = 0.025   # 期货和股票的成交率限制应该不一样
        self.volume_round = 0
        self.price_round = 2
        self.get_trade_vp = None

        self.reset_trade_id()

    @classmethod
    def reset_trade_id(cls):
        cls.trade_id = int(datetime.now().strftime("%Y%m%d%H%M%S")) * 100000

    @classmethod
    def next_trade_id(cls):
        cls.trade_id += 1
        return cls.trade_id

    def match_by_tick1(self, order, tick, trade_infos):
        """根据1档tick行情撮合"""
        last_tick = self.last_mds.get(tick.btSymbol)
        if not last_tick:
            last_tick = BtTickData()

        self.get_trade_vp = self.get_trade_vp_by_tick
        volume_delta = tick.volume - last_tick.volume
        ask_price, bid_price = tick.askPrice1, tick.bidPrice1

        self.match_order(order, ask_price, bid_price, tick.lastPrice, tick.volume, volume_delta,
                         tick.actionDay, tick.time[:8], trade_infos)

        if tick != last_tick:
            self.last_mds[tick.btSymbol] = tick

    def match_by_tick5(self, order, tick, trade_infos):
        """根据5档tick行情撮合"""
        last_tick = self.last_mds.get(tick.btSymbol)
        if not last_tick:
            last_tick = BtTickData()

        self.get_trade_vp = self.get_trade_vp_by_tick
        volume_delta = tick.volume - last_tick.volume
        
        for i in range(5):
            if i == 0:
                ask_price = tick.askPrice1
                bid_price = tick.bidPrice1
            elif i == 1:
                ask_price = tick.askPrice2
                bid_price = tick.bidPrice2
            elif i == 2:
                ask_price = tick.askPrice3
                bid_price = tick.bidPrice3
            elif i == 3:
                ask_price = tick.askPrice4
                bid_price = tick.bidPrice4
            elif i == 4:
                ask_price = tick.askPrice5
                bid_price = tick.bidPrice5

            rv = self.match_order(order, ask_price, bid_price, tick.lastPrice, tick.volume, volume_delta,
                                  tick.actionDay, tick.time[:8], trade_infos)
            if rv == 0:
                # 没有成交
                break
            volume_delta -= trade_infos[-1].trade_volume

        if tick != last_tick:
            self.last_mds[tick.btSymbol] = tick

    def match_by_bar(self, order, bar, trade_infos):
        """根据bar行情撮合"""
        # order = BtOrderData()
        # bar = BtBarData()

        self.get_trade_vp = self.get_trade_vp_by_bar
        self.match_order(order, bar.close, bar.close, bar.close, bar.volume, bar.volume,
                         bar.date, bar.time, trade_infos)

    def match_order(self, order, ask_price, bid_price, last_price, volume, volume_delta, cur_date, cur_time, trade_infos):
        """根据行情价格撮合订单"""
        # order = BtOrderData()

        # FIXME verify ask_price & bid_price

        if (order.direction == DIRECTION_LONG and order.price >= ask_price) or \
           (order.direction == DIRECTION_SHORT and order.price <= bid_price):

            if order.priceType == PRICETYPE_FOK and order.totalVolume > volume_delta:
                # 该FOK单无法成交，创建一个成交量为0的数据，后续该订单将不在挂单队列中
                order.status = STATUS_CANCELLED
                order.statusMsg = "已撤单"
                trade_info = TradeInfo(order, '', 0, 0, cur_date, cur_time)
                trade_infos.append(trade_info)
                return 0

            # !该订单可成交!
            # print("match_order for order:{} at dt:{}:{}".format(order, cur_date, cur_time))

            trade_price, trade_volume = self.get_trade_vp(order.direction, order.price,
                order.totalVolume - order.tradedVolume, volume_delta, last_price)
            if trade_volume < 0.0001:
                if order.priceType in self.PRICETYPE_TOBE_CANCELED:
                    order.status = STATUS_CANCELLED
                    order.statusMsg = "已撤单"
                    trade_info = TradeInfo(order, '', 0, 0, cur_date, cur_time)
                    trade_infos.append(trade_info)
                return 0

            # 更新订单数据
            order.tradedVolume += trade_volume
            if order.totalVolume - order.tradedVolume > 0:
                # 部分成交
                if order.priceType in self.PRICETYPE_TOBE_CANCELED:
                    order.status = STATUS_PARTCANCELLED
                    order.statusMsg = "部分撤单"
                else:
                    order.status = STATUS_PARTTRADED
                    order.statusMsg = "部分成交"
            else:
                # 全部成交
                order.status = STATUS_ALLTRADED
                order.statusMsg = "全部成交"

            # 成交信息
            trade_id = str(self.next_trade_id())
            trade_info = TradeInfo(order, trade_id, trade_volume, trade_price, cur_date, cur_time)
            trade_infos.append(trade_info)

            return 1
        elif order.priceType in self.PRICETYPE_TOBE_CANCELED:
            # 市价单/FAK/FOK则创建一个成交量为0的数据，后续该订单将不在挂单队列中
            order.status = STATUS_CANCELLED
            order.statusMsg = "已撤单"
            trade_info = TradeInfo(order, '', 0, 0, cur_date, cur_time)
            trade_infos.append(trade_info)
            return 0
        return 0

    def get_trade_vp_by_tick(self, direction, order_price, order_volume, volume, last_price):
        """根据tick获取成交价量"""
        if direction == DIRECTION_LONG:
            trade_price = min(last_price, order_price)
        else:
            trade_price = max(last_price, order_price)

        trade_volume = min(order_volume, volume)
        return trade_price, trade_volume

    def get_trade_vp_by_bar(self, direction, order_price, order_volume, volume, last_price):
        """根据bar获取成交价量"""
        max_volume = self.volume_limit * volume if self.volume_limit > 0 else volume
        trade_volume = min(order_volume, max_volume)
        if self.volume_round == 1:
            trade_volume = int(trade_volume)
        elif self.volume_round > 1:
            trade_volume = int(trade_volume / self.volume_round * self.volume_round)
        else:
            pass

        volume_share = min(trade_volume / volume, self.volume_limit)
        simulated_impact = volume_share ** 2 \
            * math.copysign(self.price_impact, direction == DIRECTION_LONG) \
            * order_price
        impacted_price = order_price + simulated_impact

        trade_price = round(impacted_price, self.price_round)
        return trade_price, trade_volume


class VMatch(object):
    """单账户的模拟撮合数据等"""
    # 交易所报单编号
    order_sysid = 0

    def __init__(self, is_future=True):
        """是否需要每个该类实例只对应一个市场
        """
        self.vmatch_engine = VMatchEngine()
        self.trading_day = ''
        self.order_dicts = {}   # {symbol1:[order_list]}

        self.is_future = is_future
        if is_future:
            self.check_position_closeable = self.check_future_position_closeable
        else:
            self.check_position_closeable = self.check_equity_position_closeable

        # callbacks
        self.rtn_order_func = None
        self.rtn_trade_func = None
        self.rtn_userdata = None

        self.new_orders = []    # 新订单
        self.open_orders = []   # 挂单

        self.pos_dicts = {}     # 持仓记录 {symbol:SimPosition}
        self.max_order_ref = 0  # 客户端最大报单编号
        self.frontID = 1
        self.sessionID = int(datetime.now().strftime("%Y%m%d%H%M%S")) % 1000000000000

        # 交易流水
        self.all_trades = []
        self.all_datas = []

    @classmethod
    def reset_sysid(cls):
        """重置系统报单编号"""
        cls.order_sysid = int(datetime.now().strftime("%Y%m%d%H%M%S")) * 100000

    @classmethod
    def next_sysid(cls):
        """系统报单编号"""
        cls.order_sysid += 1
        return cls.order_sysid

    def set_trading_day(self, trading_day):
        """设置交易日"""
        if self.trading_day != trading_day:
            self.order_dicts.clear()
            self.new_orders.clear()
            self.open_orders.clear()
            self.reset_sysid()
        self.trading_day = trading_day

    def set_rtn_func(self, rtn_order_func, rtn_trade_func, rtn_userdata):
        """设置回调函数"""
        self.rtn_order_func = rtn_order_func
        self.rtn_trade_func = rtn_trade_func
        self.rtn_userdata = rtn_userdata

    def req_input_order(self, order_req):
        """有新订单请求
        TODO: 是否可支持同步模式，直接返回一确认信息
        """
        order = self.gen_order_data(order_req)
        self.new_orders.append(order)

    def req_cancel_order(self, cancel_req):
        """撤单请求"""
        # 根据委托号从挂单中撤销掉
        pass

    def on_new_tick(self, tick):
        """有新1档tick行情到达"""
        # tick = BtTickData()

        self._process_new_orders()

        try:
            orders = self.order_dicts[tick.btSymbol]
        except KeyError:
            return

        # 没有挂单
        if len(orders) == 0:
            return

        trade_infos = []
        for order in orders:
            self.vmatch_engine.match_by_tick1(order, tick, trade_infos)

        for trade_info in trade_infos:
            # 从挂单队列中移除
            try:
                orders.remove(trade_info.order)
            except ValueError:
                pass

            self.all_datas.append(trade_info.traded_order)
            if trade_info.trade_volume:
                trade = self.gen_trade_data(trade_info)
                self.all_trades.append(trade)
                self.all_datas.append(trade)
            else:
                trade = None

            # 委托通知
            if self.rtn_order_func:
                self.rtn_order_func(self.rtn_userdata, trade_info.traded_order)

            # 成交通知
            if self.rtn_trade_func and trade:
                self.rtn_trade_func(self.rtn_userdata, trade)

    def on_new_bar(self, bar):
        """有新bar行情到达"""
        # bar = BtBarData()

        self._process_new_orders()

        try:
            orders = self.order_dicts[bar.btSymbol]
        except KeyError:
            return

        # 没有挂单
        if len(orders) == 0:
            return

        trade_infos = []
        for order in orders:
            self.vmatch_engine.match_by_bar(order, bar, trade_infos)

        for trade_info in trade_infos:
            # 从挂单队列中移除
            try:
                orders.remove(trade_info.order)
            except ValueError:
                pass

            self.all_datas.append(trade_info.traded_order)
            if trade_info.trade_volume:
                trade = self.gen_trade_data(trade_info)
                self.all_trades.append(trade)
                self.all_datas.append(trade)
            else:
                trade = None

            # 委托通知
            if self.rtn_order_func:
                self.rtn_order_func(self.rtn_userdata, trade_info.traded_order)

            # 成交通知
            if self.rtn_trade_func and trade:
                self.rtn_trade_func(self.rtn_userdata, trade)

    def _process_new_orders(self):
        """处理新的订单请求"""
        for order in self.new_orders:
            btSymbol = order.btSymbol

            # order.orderTime = self.currentTime
            # order.insertDate = self.currentDate
            # order.orderDateTime = ' '.join([order.insertDate, order.orderTime])
            order.frontID = self.frontID
            order.sessionID = self.sessionID

            try:
                simpos = self.pos_dicts[btSymbol]
            except KeyError:
                simpos = SimPosition(order.multiplier, self.is_future)
                self.pos_dicts[btSymbol] = simpos

            if not self.check_position_closeable(order, simpos, do_freeze=True):
                order.status = STATUS_REJECTED
                order.statusMsg = "可平仓位不足"
            else:
                order.status = STATUS_NOTTRADED
                order.statusMsg = "未成交"

                # 生成系统报单编号
                order.orderSysID = str(self.next_sysid())

            # 放入挂单队列中
            if order.status != STATUS_REJECTED:
                try:
                    working_orders = self.order_dicts[btSymbol]
                    working_orders.append(order)
                except KeyError:
                    working_orders = [order]
                    self.order_dicts[btSymbol] = working_orders

            # 委托确认通知
            if self.rtn_order_func:
                self.rtn_order_func(self.rtn_userdata, order)

        self.new_orders.clear()

    @staticmethod
    def gen_order_data(order_req):
        """创建一笔委托数据"""
        order = BtOrderData()
        order.gatewayName = order_req.gatewayName
        order.accountID = order_req.accountID
        order.brokerID = order_req.brokerID
        order.symbol = order_req.symbol
        order.exchange = order_req.exchange     # TODO: maybe need fix exchange
        order.btSymbol = order_req.btSymbol
        order.orderID = str(order_req.orderID)
        order.businessUnit = ''
        order.direction = order_req.direction
        order.offset = order_req.offset
        order.hedgeFlag = '1'
        order.priceType = order_req.priceType
        order.price = order_req.price
        order.totalVolume = order_req.volume
        order.tradedVolume = 0
        order.status = STATUS_UNKNOWN
        order.statusMsg = "未知"
        # order.tradingDay = trading_day
        # order.orderTime = self.currentTime
        # order.insertDate = self.currentDate
        # order.orderDateTime = ' '.join([order.insertDate, order.orderTime])
        order.userID = order_req.userID
        order.multiplier = order_req.multiplier
        # order.orderKey = (int(order.orderID), order.frontID, order.sessionID)
        return order

    @staticmethod
    def gen_trade_data(trade_info):
        """ 创建一个成交数据对象
        trade_info: TradeInfo
        """
        # original order object
        order = trade_info.order

        trade = BtTradeData()
        trade.accountID = order.accountID
        trade.brokerID = order.brokerID
        trade.symbol = order.symbol
        trade.exchange = order.exchange
        trade.btSymbol = order.btSymbol
        trade.orderSysID = order.orderSysID
        trade.btOrderSysID = order.btOrderSysID
        trade.tradeID = trade_info.trade_id
        trade.btTradeID = '.'.join([trade.exchange, trade.tradeID])
        trade.orderID = order.orderID
        trade.btOrderID = order.btOrderID
        trade.direction = order.direction
        trade.offset = order.offset
        trade.price = trade_info.trade_price
        trade.volume = trade_info.trade_volume
        trade.tradeDate = trade_info.trade_date
        trade.tradeTime = trade_info.trade_time
        trade.tradingDay = order.tradingDay
        trade.tradeDateTime = ' '.join([trade.tradeDate, trade.tradeTime])
        # trade.businessUnit = order.businessUnit
        trade.userID = order.userID
        return trade

    @staticmethod
    def check_future_position_closeable(order, simpos, do_freeze=False):
        """检查期货是否有持仓可平"""
        if order.offset != OFFSET_OPEN:
            residual_volume = order.totalVolume
            if (order.direction == DIRECTION_LONG and residual_volume > simpos.short_avail) or \
               (order.direction == DIRECTION_SHORT and residual_volume > simpos.long_avail):
                # 拒单
                order.status = STATUS_CANCELLED
                order.statusMsg = "废单：可平仓位不够"
                return False

            if do_freeze:
                if order.direction == DIRECTION_LONG:
                    simpos.update_short_frozen(residual_volume)
                else:
                    simpos.update_long_frozen(residual_volume)
        return True

    @staticmethod
    def check_equity_position_closeable(order, simpos, do_freeze=False):
        """检查股票是否有持仓可平"""
        residual_volume = order.totalVolume
        if residual_volume > simpos.long_avail:
            # 拒单
            order.status = STATUS_CANCELLED
            order.statusMsg = "废单：可平仓位不够"
            return False

        if do_freeze:
            simpos.update_long_frozen(residual_volume)
        return True

class VMatchManager(object):
    """
    模拟撮合管理，负责行情的接入与各个账户的管理
    1. 可以本地读tick行情，依次触发
    2. 可以接实时tick行情，被动触发
    """
    def __init__(self):
        # 管理多个账户的撮合
        self.vmatch_dicts = {}
        self.trading_day = ''

        self.order_userdata = None
        self.order_callback = None
        self.trade_userdata = None
        self.trade_callback = None

        self.__active = False
        self.__que = Queue()
        self.__thrd = Thread(target=self.work_run)

    def set_trading_day(self, trading_day):
        """设置交易日"""
        self.trading_day = trading_day
        for vmatch in self.vmatch_dicts.values():
            vmatch.set_trading_day(trading_day)

    def set_order_callback(self, callback, userdata):
        self.order_callback = callback
        self.order_userdata = userdata

    def set_trade_callback(self, callback, userdata):
        self.trade_callback = callback
        self.trade_userdata = userdata

    def req_input_order(self, order_req):
        """有新订单请求
        TODO: 是否可支持同步模式，直接返回一确认信息
        """
        vmatch = self.vmatch_dicts.get(order_req.accountID)
        if not vmatch:
            vmatch = VMatch(is_future=True)
            vmatch.set_rtn_func(self.on_rtn_order, self.on_rtn_trade, self)
            self.vmatch_dicts[order_req.accountID] = vmatch
        vmatch.req_input_order(order_req)

    def req_cancel_order(self, cancel_req):
        """撤单请求"""
        # 根据委托号从挂单中撤销掉
        vmatch = self.vmatch_dicts.get(order_req.accountID)
        if not vmatch:
            return
        vmatch.req_cancel_order(cancel_req)

    def on_new_tick(self, tick):
        """新行情"""
        for vmatch in self.vmatch_dicts.values():
            vmatch.on_new_tick(tick)

    def on_new_bar(self, bar):
        """新行情"""
        for vmatch in self.vmatch_dicts.values():
            vmatch.on_new_bar(bar)

    def on_rtn_order(self, userdata, order):
        """订单回报"""
        if self.order_callback:
            self.order_callback(self.order_userdata, order)

    def on_rtn_trade(self, userdata, trade):
        """成交回报"""
        if self.trade_callback:
            self.trade_callback(self.trade_userdata, trade)

    def work_run(self):
        """行情工作线程"""
        while self.__active:
            try:
                event = self.__que.get(timeout=1)

                # 处理事件
                self.on_new_tick(event.data)
            except Empty:
                continue

class QuoteEngine(object):
    """行情引擎 (一些接口为示例代码)
    1. 读文件
    2. 接实时行情
    """
    def __init__(self, vmatchmgr):
        self.vmatchmgr = vmatchmgr
        self.tick_list = []

    def put_ticks(self, tick_list, clear_previous=False):
        """放入行情列表"""
        if clear_previous:
            self.tick_list.clear()
        self.tick_list.extend(tick_list)

    def read_csv(self, csv_file):
        """读取csv行情文件"""
        pass

    def cast_quotes(self):
        last_tick_date = ''
        for tick in self.tick_list:
            if last_tick_date != tick.date:
                vmatchmgr.set_trading_day(tick.date)
                last_tick_date = tick.date
            vmatchmgr.on_new_tick(tick)



class VMatchExchange(object):
    """模拟交易所，
    保存买卖挂单队列，有订单则发出一笔行情，撮合则也产生一笔行情
    """
    order_sysid = 1
    trade_id = 1

    def __init__(self):
        self.buy_order_dicts = {}
        self.sell_order_dicts = {}
        self.traded_orders = {}

        self.trading_day = ''

        # TODO: 应保存所有的交易流水，跨交易日时应清除所有挂单

        # callbacks
        self.rtn_tick_func = None
        self.rtn_order_func = None
        self.rtn_trade_func = None
        self.rtn_userdata = None

        self.__active = False
        self.__que = Queue()
        self.__thrd = Thread(target=self.work_run)

    @classmethod
    def next_sys_id(cls):
        cls.order_sysid += 1
        return cls.order_sysid

    @classmethod
    def next_trade_id(cls):
        cls.trade_id += 1
        return cls.trade_id

    def get_buy_order_list(self, symbol):
        """获取挂单列表"""
        return self.buy_order_dicts.get(symbol, list())

    def get_sell_order_list(self, symbol):
        """获取挂单列表"""
        return self.sell_order_dicts.get(symbol, list())

    def set_rtn_func(self, rtn_order_func, rtn_trade_func, rtn_userdata):
        """设置回调函数"""
        self.rtn_order_func = rtn_order_func
        self.rtn_trade_func = rtn_trade_func
        self.rtn_userdata = rtn_userdata

    def req_input_order(self, order_req):
        """订单请求"""
        order_data = VMatch.gen_order_data(order_req)

        if self.__thrd:
            self.__que.put((EV_REQ_ORDER, order_data))
        else:
            self.do_match(order_data)

    def req_cancel_order(self, cancel_req):
        """撤单请求"""
        if self.__thrd:
            self.__que.put((EV_REQ_CANCEL, cancel_req))
        else:
            self.do_match(cancel_req)

    def do_cancel(self, cancel_req):
        """执行挂单的撤销"""
        original_order = None
        buy_orders = self.get_buy_order_list(cancel_req.btSymbol)
        for buy_order in buy_orders:
            if buy_order.orderSysID == cancel_req.orderSysID:
                original_order = buy_order
                buy_orders.remove(buy_order)
                break

        if not original_order:
            sell_orders = self.get_sell_order_list(cancel_req.btSymbol)
            for sell_order in sell_orders:
                if sell_order.orderSysID == cancel_req.orderSysID:
                    original_order = sell_orders
                    sell_orders.remove(sell_order)
                    break

        if original_order:
            # 撤销成功
            if original_order.tradedVolume > 0:
                original_order.status = STATUS_PARTCANCELLED
                original_order.statusMsg = "部分撤单"
            else:
                original_order.status = STATUS_CANCELLED
                original_order.statusMsg = "全部撤单"
            if self.rtn_order_func:
                self.rtn_order_func(self.rtn_userdata, original_order)
        else:
            # TODO: 撤单失败(不存在/已成交)
            pass

    def do_match(self, order):
        """执行买卖挂单的撮合"""
        buy_orders = self.get_buy_order_list(order.btSymbol)
        sell_orders = self.get_sell_order_list(order.btSymbol)
        pruned_orders = []

        if order.direction == DIRECTION_LONG:
            # 与卖单比较，若能撮合，则生成成交，否则插入订单到适合位置（价格优化，时间优化）
            for sell_order in sell_orders:
                if order.price < sell_order.price:
                    break

                # 成交
                self.process_match_data(order, sell_order, sell_order.price)
                if sell_order.status == STATUS_ALLTRADED:
                    pruned_orders.append(sell_order)

            # 移除挂单
            for prune_order in pruned_orders:
                sell_orders.remove(prune_order)

            # 插入到挂单队列中（以价格优先，时间优先）
            if order.status == STATUS_NOTTRADED or order.status == STATUS_PARTTRADED:
                self.insert_pending_order(buy_orders, order, is_buy=True)
        else:
            # 与买单比较，若能撮合，则生成成交，否则插入订单到适合位置
            for buy_order in buy_orders:
                if order.price > buy_order.price:
                    break

                # 成交
                self.process_match_data(buy_order, order, buy_order.price)
                if buy_order.status == STATUS_ALLTRADED:
                    pruned_orders.append(buy_order)

            # 移除挂单
            for prune_order in pruned_orders:
                buy_orders.remove(prune_order)

            # 插入到挂单队列中（以价格优先，时间优先）,TODO: 处理 FAK/FOK单
            if order.status == STATUS_NOTTRADED or order.status == STATUS_PARTTRADED:
                self.insert_pending_order(sell_orders, order, is_buy=False)

    def insert_pending_order(self, order_list, order, is_buy):
        """处理挂单"""
        index = 0
        cmp = lambda x, y: x >= y if is_buy else x <= y
        for temp_order in order_list:
            if cmp(temp_order.price, order.price):
                index += 1
                continue
            order_list.insert(index, order)
            break
        if index == len(order_list):
            order_list.append(order)

    def process_match_data(self, buy_order, sell_order, trade_price):
        """处理成交数据"""
        # 成交数据
        trade_id = str(self.next_trade_id())
        trade_time = datetime.now().strftime("%H:%M:%S")
        trade_volume = min(buy_order.totalVolume - buy_order.tradedVolume,
                           sell_order.totalVolume - sell_order.tradedVolume)
        buy_order.tradedVolume += trade_volume
        sell_order.tradedVolume += trade_volume

        if buy_order.totalVolume == buy_order.tradedVolume:
            buy_order.status = STATUS_ALLTRADED
            buy_order.statusMsg = "全部成交"
        else:
            buy_order.status = STATUS_PARTTRADED
            buy_order.statusMsg = "部分成交"

        if sell_order.totalVolume == sell_order.tradedVolume:
            sell_order.status = STATUS_ALLTRADED
            sell_order.statusMsg = "全部成交"
        else:
            sell_order.status = STATUS_PARTTRADED
            sell_order.statusMsg = "部分成交"

        buy_trade_info = TradeInfo(buy_order, trade_id, trade_volume, trade_price,
                                   self.trading_day, trade_time)
        buy_trade = VMatch.gen_trade_data(buy_trade_info)
        sell_trade_info = TradeInfo(sell_order, trade_id, trade_volume, trade_price,
                                    self.trading_day, trade_time)
        sell_trade = VMatch.gen_trade_data(sell_trade_info)

        # 成交通知
        if self.rtn_order_func:
            self.rtn_order_func(self.rtn_userdata, buy_order)
            self.rtn_order_func(self.rtn_userdata, sell_order)
        if self.rtn_trade_func:
            self.rtn_trade_func(self.rtn_userdata, buy_trade)
            self.rtn_trade_func(self.rtn_userdata, sell_trade)

        # 产生tick行情
        """
        tick = BtTickData()
        tick.symbol = buy_order.symbol
        tick.exchange = buy_order.exchange
        tick.btSymbol = buy_order.btSymbol
        tick.lastPrice = trade_price
        tick.volume += trade_volume
        tick.tradingDay = self.trading_day
        tick.time = trade_time
        if self.rtn_tick_func:
            self.rtn_tick_func(self.rtn_userdata, tick)
        """

    def work_run(self):
        """工作线程"""
        while self.__active:
            try:
                item = self.__que.get(timeout=1)
                if item is None:
                    continue

                if item[0] == EV_REQ_ORDER:
                    self.do_match(item[1])
                elif item[0] == EV_REQ_CANCEL:
                    self.do_cancel(item[1])
            except Empty:
                continue


############################################################
def process_rtn_order(userdata, order):
    print("rtn_order:", order)

def process_rtn_trade(userdata, trade):
    print("rtn_trade:", trade)

if __name__ == "__main__":
    ticks = []
    tick1 = BtTickData()
    tick1.btSymbol = "rb1905"
    tick1.volume = 5
    tick1.askPrice1 = 3984
    tick1.bidPrice1 = 3981
    tick1.lastPrice = 3982
    tick1.time = "10:12:12"
    tick1.actionDay = "2019-01-03"
    ticks.append(tick1)

    order_req = BtOrderReq()
    order_req.gatewayName = "CTP"
    order_req.accountID = "038313"
    order_req.btSymbol = "rb1905"
    order_req.price = 3984
    order_req.volume = 1
    order_req.direction = DIRECTION_LONG
    order_req.offset = OFFSET_OPEN
    order_req.multiplier = 10

    vmatchmgr = VMatchManager()
    vmatchmgr.set_order_callback(process_rtn_order, None)
    vmatchmgr.set_trade_callback(process_rtn_trade, None)
    vmatchmgr.req_input_order(order_req)

    qe = QuoteEngine(vmatchmgr)
    qe.put_ticks(ticks)
    qe.cast_quotes()

    print("tested!")
