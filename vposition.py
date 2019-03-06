# encoding: UTF-8
#
# Copyright 2018 BigQuant, Inc.
#

from copy import copy

from bigvmatch.vmatch.vtypes import *

from bigtrader.btObject import BtPositionData, BtPositionDetailData

WORKING_STATUS = [Status.Unknown, Status.Pending, Status.PartFilled]
FINISHED_STATUS = [Status.Filled, Status.Rejected, Status.Cancelled]


"""
持仓接口：规定持仓必须处理 on_order/on_trade/on_cancel 等事件
    分股票持仓/期货持仓实现，用于管理不同产品类型的持仓
"""

class PositionInfo(object):
    """单边持仓信息"""
    def __init__(self, symbol):
        self.symbol = symbol
        self.position = 0
        self.price = 0

class VPosition(object):
    def __init__(self, symbol):
        pass

    def on_order(self, order):
        raise NotImplementedError("on_order")

    def on_trade(self, trade):
        raise NotImplementedError("on_trade")

class PositionStock(VPosition):
    """股票持仓"""
    def __init__(self, symbol):
        super(PositionStock, self).__init__(symbol)
        self.pos_info = PositionInfo(symbol)

    def on_order(self, order):
        """处理报单信息"""
        # 1. 平仓单（卖出单）：冻结持仓数量
        # 2. 撤单确认：解冻持仓数量
        # 3. 其它直接返回
        pass

    def on_trade(self, trade):
        """处理成交信息"""
        # 1. 开仓则累加持仓，并更新持仓均价/持仓成本等
        # 2. 平仓则累减持仓，为简化暂时不使用持仓明细更新
        pass

    def get_position(self):
        return self.pos_info

class PositionFuture(VPosition):
    """期货持仓"""
    def __init__(self, symbol):
        super(PositionFuture, self).__init__(symbol)
        self.long_position = PositionInfo(symbol)
        self.short_position = PositionInfo(symbol)

    def on_order(self, order):
        """处理报单信息"""
        # 1. 平仓单（卖出单）：冻结持仓数量
        # 2. 撤单确认：解冻持仓数量
        # 3. 其它直接返回
        pass

    def on_trade(self, trade):
        """处理成交信息"""
        # 1. 开仓则累加持仓，并更新持仓均价/持仓成本等
        # 2. 平仓则累减持仓，为简化暂时不使用持仓明细更新
        pass

    def get_long_position(self):
        return self.long_position

    def get_short_position(self):
        return self.short_position


########################################################################
class VPosition2(object):
    """持仓信息"""

    def __init__(self, accountID, contract):
        """Constructor"""
        self.brokerID = ''
        self.accountID = ''

        self.symbol = ''
        self.exchange = ''
        self.multiplier = contract.multiplier
        self.priceTick = contract.priceTick
        self.decimal = 2

        self._contract = contract
        self.btSymbol = contract.btSymbol
        self.symbol = contract.symbol
        self.exchange = contract.exchange
        self.name = contract.name
        self.multiplier = contract.multiplier
        self.priceTick = contract.priceTick
        self.decimal = 2

        self.marginRate = None
        self.commRate = None

        # 最新建仓时间
        self.latestPosDateTime = None

        # 已完成的订单的号 <btOrderSysID> 
        self.finishedOrderSet = set()

        # 持仓明细
        self.positionDetails = []

        # 多仓
        self._longPos = 0
        self._longYdPos = 0
        self._longTdPos = 0
        self._longPosFrozen = 0
        self._longYdFrozen = 0
        self._longTdFrozen = 0
        self._longPnl = 0.0
        self._longPrice = 0.0
        self._longMargin = 0.0
        self._longUpdateTime = None

        # 空仓
        self._shortPos = 0
        self._shortYdPos = 0
        self._shortTdPos = 0
        self._shortPosFrozen = 0
        self._shortYdFrozen = 0
        self._shortTdFrozen = 0
        self._shortPnl = 0.0
        self._shortPrice = 0.0
        self._shortMargin = 0.0
        self._shortUpdateTime = None

        # 最新价
        self.lastPrice = 0.0
        self.tradingDay = ''
        self.realizedPnl = 0.0
        # tick行情更新次数
        self.tickUpdateN = 0

    def __repr__(self):
        return "Position({},longPos:{},longYdPos:{},longFrozen:{},longPnl:{},longPrice:{},\
    shortPos:{},shortYdPos:{},shortFrozen:{},shortPnl:{},shortPrice:{},lastPrice:{})"\
               .format(self.btSymbol, self._longPos, self._longYdPos, self._longPosFrozen, self._longPnl, self._longPrice,
                       self._shortPos, self._shortYdPos, self._shortPosFrozen, self._shortPnl, self._shortPrice, self.lastPrice)

    def reset(self):
        """更新保证金率"""
        self.finishedOrderSet.clear()

    def set_log_prefix(self, prefix):
        """设置日志前缀"""
        if not prefix:
            return
        self.logPrefix = prefix

    def update_margin_rate(self, marginRate):
        """更新保证金率"""
        if not marginRate:
            return

        assert self.btSymbol == marginRate.btSymbol, "update_margin_rate btSymbol not equal"
        self.marginRate = marginRate

    def update_trading_day(self, tradingDay):
        """更新交易日"""
        self.tradingDay = tradingDay

    #----------------------------------------------------------------------
    @property
    def net_pos(self):
        """获取净持仓，正数为多仓，负数为空仓"""
        return self._longPos - self._shortPos

    @property
    def net_price(self):
        """获取净持仓价格"""
        if self.net_pos == 0:
            return 0.0
        return abs((self._longPos * self._longPrice - self._shortPos * self._shortPrice) / self.net_pos)

    @property
    def long_pos(self):
        return self._longPos

    @property
    def short_pos(self):
        return self._shortPos

    @property
    def long_avail(self):
        return self._longPos - self._longPosFrozen

    @property
    def short_avail(self):
        return self._shortPos - self._shortPosFrozen

    @property
    def long_margin(self):
        return self._longMargin

    @property
    def short_margin(self):
        return self._shortMargin

    @property
    def long_price(self):
        return self._longPrice

    @property
    def short_price(self):
        return self._shortPrice

    @property
    def long_pnl(self):
        return self._longPnl

    @property
    def short_pnl(self):
        return self._shortPnl

    @property
    def realized_pnl(self):
        return self.realizedPnl

    @property
    def is_account_pos(self):
        return self.isAccountPos

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, contract):
        self._contract = contract
        self.btSymbol = contract.btSymbol
        self.symbol = contract.symbol
        self.exchange = contract.exchange
        self.name = contract.name
        self.multiplier = contract.multiplier
        self.priceTick = contract.priceTick

    #----------------------------------------------------------------------
    def process_order_query_rsp(self, order):
        """处理订单查询回报"""
        if order.status in FINISHED_STATUS:
            return

        volume = order.totalVolume - order.tradedVolume
        rv = self.process_order_req(order.direction, order.offset, volume)
        assert rv is True, 'process_order_query_rsp {},{},{} failed'\
               .format(order.accountID, order.symbol, volume)

    def process_order_req(self, direction, offset, volume):
        """发单更新，持仓冻结"""
        if offset == OFFSET_OPEN:
            return True

        # (允许一次重复平仓 'and'之后的逻辑)
        if direction == Direction.Long:
            # 平空仓
            if volume > (self._shortPos - self._shortPosFrozen) and self._shortPosFrozen > self._shortPos:
                return False

            if offset == OFFSET_CLOSE or offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._shortYdPos:
                    self._shortTdFrozen += volume - self._shortYdPos
                    self._shortYdFrozen = self._shortYdPos
                else:
                    self._shortYdFrozen += volume
            elif offset == OFFSET_CLOSETODAY:
                if volume > (self._shortTdPos - self._shortTdFrozen) and self._shortTdFrozen > self._shortTdPos:
                    return False
                self._shortTdFrozen += volume
            self._shortPosFrozen += volume
            self.pos_log(LEVEL_INFO, '*position by req close short vol:{} shortPos:{},shortFrozen:{},shortYdFrozen:{},shortTdFrozen:{}'\
                         .format(volume, self._shortPos, self._shortPosFrozen, self._shortYdFrozen, self._shortTdFrozen))
        elif direction == Direction.Short:
            # 平多仓
            if volume > (self._longPos - self._longPosFrozen) and self._longPosFrozen > self._longPos:
                return False

            if offset == OFFSET_CLOSE or offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._longYdPos:
                    self._longTdFrozen += volume - self._longYdPos
                    self._longYdFrozen = self._longYdPos
                else:
                    self._longYdFrozen += volume
            elif offset == OFFSET_CLOSETODAY:
                if volume > (self._longTdPos - self._longTdFrozen) and self._longTdFrozen > self._longTdPos:
                    return False
                self._longTdFrozen += volume
            self._longPosFrozen += volume
            self.pos_log(LEVEL_INFO, '*position by req close long vol:{} longPos:{},longFrozen:{},longYdFrozen:{},longTdFrozen:{}'\
                         .format(volume, self._longPos, self._longPosFrozen, self._longYdFrozen, self._longTdFrozen))

        # freeze success
        return True

    def process_order_finished(self, order):
        """处理订单回报，持仓解冻
        """
        if order.offset == OFFSET_OPEN:
            return

        # 仅处理撤单和拒单，解冻冻结数量
        if order.status != STATUS_CANCELLED and order.status != STATUS_REJECTED:
            return

        # 订单已处理过
        if order.btOrderSysID in self.finishedOrderSet:
            return
        self.finishedOrderSet.add(order.btOrderSysID)

        volume = order.totalVolume - order.tradedVolume
        if order.direction == Direction.Long:
            # 平空仓
            self._shortPosFrozen -= volume
            if order.offset == OFFSET_CLOSE or order.offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._shortYdFrozen:
                    self._shortTdFrozen -= volume - self._shortYdFrozen
                    self._shortYdFrozen = 0
                else:
                    self._shortYdFrozen -= volume
            elif order.offset == OFFSET_CLOSETODAY:
                    self._shortTdFrozen -= volume
            self.pos_log(LEVEL_INFO, '*position by cancel short vol:{} shortPos:{},shortFrozen:{},shortYdFrozen:{},shortTdFrozen:{}'\
                         .format(volume, self._shortPos, self._shortPosFrozen, self._shortYdFrozen, self._shortTdFrozen))
        elif order.direction == Direction.Short:
            # 平多仓
            self._longPosFrozen -= volume
            if order.offset == OFFSET_CLOSE or order.offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._longYdFrozen:
                    self._longTdFrozen -= volume - self._longYdFrozen
                    self._longYdFrozen = 0
                else:
                    self._longYdFrozen -= volume
            elif order.offset == OFFSET_CLOSETODAY:
                self._longTdFrozen -= volume
            self.pos_log(LEVEL_INFO, '*position by cancel long vol:{} longPos:{},longFrozen:{},longYdFrozen:{},longTdFrozen:{}'\
                         .format(volume, self._longPos, self._longPosFrozen, self._longYdFrozen, self._longTdFrozen))

    def process_order_trade(self, trade):
        """处理成交回报，更新本地持仓详情"""
        volume = trade.volume
        price = trade.price
        direction = trade.direction
        offset = trade.offset

        # 保证金
        margin = self.calculate_margin(direction, volume, price)

        # 开仓保存一条明细
        if offset == OFFSET_OPEN:
            _posDetail = self._make_position_detail_data(trade, margin)
            self.positionDetails.append(_posDetail)

        # 平仓盈亏
        realizedPnl = 0.0

        if direction == Direction.Long and offset == OFFSET_OPEN:
            # 开多仓
            cost = self._longPrice * self._longPos
            self._longPos += volume
            self._longTdPos += volume
            self._longMargin += margin

            # 开仓时重新计算持仓均价
            cost += volume * price
            self._longPrice = cost / self._longPos
            self._longUpdateTime = trade.tradeTime
            self.pos_log(LEVEL_INFO, '*position by trade open long px:{},vol:{} longPos:{},longMargin:{},longPrice:{},longPnl:{}'\
                         .format(price, volume, self._longPos, self._longMargin, self._longPrice, self._longPnl))
        elif direction == Direction.Short and offset == OFFSET_OPEN:
            # 开空仓
            cost = self._shortPrice * self._shortPos
            self._shortPos += volume
            self._shortTdPos += volume
            self._shortMargin += margin

            # 开仓时重新计算持仓均价
            cost += volume * price
            self._shortPrice = cost / self._shortPos
            self._shortUpdateTime = trade.tradeTime
            self.pos_log(LEVEL_INFO, '*position by trade open short px:{},vol:{} shortPos:{},shortMargin:{},shortPrice:{},shortPnl:{}'\
                         .format(price, volume, self._shortPos, self._shortMargin, self._shortPrice, self._shortPnl))
        elif direction == Direction.Long:
            # 平空仓
            self._shortPos -= volume
            self._shortPosFrozen -= volume
            #realizedPnl = self.calculate_realized_pnl(direction, price, volume)

            if offset == OFFSET_CLOSE or offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._shortYdPos:
                    self._shortTdPos -= volume - self._shortYdPos
                    self._shortTdFrozen -= volume - self._shortYdPos

                    self._shortYdPos = 0
                    self._shortYdFrozen = 0
                else:
                    self._shortYdPos -= volume
                    self._shortYdFrozen -= volume
            elif offset == OFFSET_CLOSETODAY:
                self._shortTdPos -= volume
                self._shortTdFrozen -= volume

            # 实际持仓明细更新
            realizedPnl, margin = self.close_position_detail_data(trade)
            self._shortPrice = self.calculate_position_price(Direction.Short)
            self.realizedPnl += realizedPnl

            self._shortMargin -= margin
            if abs(self._shortPos) < 0.00000001:
                self._shortMargin = 0.0

            self._shortUpdateTime = trade.tradeTime
            self.pos_log(LEVEL_INFO, '*position by trade close short px:{},vol:{} shortPos:{},shortMargin:{},shortPnl:{},rpnl:{}'\
                         .format(price, volume, self._shortPos, self._shortMargin, self._shortPnl, realizedPnl))
        elif direction == Direction.Short:
            # 平多仓
            self._longPos -= volume
            self._longPosFrozen -= volume
            #realizedPnl = self.calculate_realized_pnl(direction, price, volume)

            if offset == OFFSET_CLOSE or offset == OFFSET_CLOSEYESTERDAY:
                if volume > self._longYdPos:
                    self._longTdPos -= volume - self._longYdPos
                    self._longTdFrozen -= volume - self._longYdPos

                    self._longYdPos = 0
                    self._longYdFrozen = 0
                else:
                    self._longYdPos -= volume
                    self._longYdFrozen -= volume
            elif offset == OFFSET_CLOSETODAY:
                self._longTdPos -= volume
                self._longTdFrozen -= volume

            # 实际持仓明细更新
            realizedPnl, margin = self.close_position_detail_data(trade)
            self._longPrice = self.calculate_position_price(Direction.Long)
            self.realizedPnl += realizedPnl

            self._longMargin -= margin
            if abs(self._longPos) < 0.00000001:
                self._longMargin = 0.0

            self._longUpdateTime = trade.tradeTime
            self.pos_log(LEVEL_INFO, '*position by trade close long px:{},vol:{} longPos:{},longMargin:{},longPnl:{},rpnl:{}'\
                         .format(price, volume, self._longPos, self._longMargin, self._longPnl, realizedPnl))

        return realizedPnl

    #----------------------------------------------------------------------
    def process_position_update(self, pos):
        """持仓查询返回时的持仓更新"""
        assert self.btSymbol == pos.btSymbol, \
               'process_position_update self symbol {} != {}'\
                    .format(self.btSymbol, pos.btSymbol)

        if pos.direction == Direction.Long:
            self._longPos = pos.position
            self._longYdPos = pos.ydPosition
            self._longTdPos = self._longPos - self._longYdPos
            self._longPnl = pos.positionPnl
            self._longPrice = pos.price
            self._longMargin = pos.useMargin
            self._longPosFrozen = pos.frozen
        elif pos.direction == Direction.Short:
            self._shortPos = pos.position
            self._shortYdPos = pos.ydPosition
            self._shortTdPos = self._shortPos - self._shortYdPos
            self._shortPnl = pos.positionPnl
            self._shortPrice = pos.price
            self._shortMargin = pos.useMargin
            self._shortPosFrozen = pos.frozen
        else:
            self.pos_log(LEVEL_ERROR, 'process_position_update unknown direction {} for {}'\
                         .format(pos.direction, pos.btSymbol))

    def process_position_detail_update(self, posDetail):
        """持仓明细查询返回"""
        self.positionDetails.append(posDetail)
        self.latestPosDateTime = max(self.latestPosDateTime, posDetail.openDateTime)

    def update_position_by_detail(self, posDetail):
        """从持仓明细中更新持仓，比如用于更新策略持仓"""
        assert self.btSymbol == posDetail.btSymbol, \
               'update_position_by_detail self symbol {} != {}'\
                    .format(self.btSymbol, posDetail.btSymbol)

        # 逐日盯市平仓盈亏（包含了手动平掉的策略的持仓）
        self.realizedPnl += posDetail.closeProfitByDate

        if posDetail.volume <= 0:
            return

        # 保存持仓明细
        posDetail = copy(posDetail)
        self.positionDetails.append(posDetail)

        # 策略冻结数量需要从挂单中获取

        # 是否为昨仓
        isYdPosition = True if posDetail.positionDate == POSITION_DATE_YESTERDAY else False
        price = posDetail.positionPrice
        volume = posDetail.volume

        if posDetail.direction == Direction.Long:
            self._longPrice = (self._longPrice * self._longPos + volume * price) / (self._longPos + volume)
            self._longPos += volume
            if isYdPosition:
                self._longYdPos += volume
            self._longTdPos = self._longPos - self._longYdPos
            self._longMargin = self.calculate_margin(Direction.Long, self._longPos, self._longPrice)
        elif posDetail.direction == Direction.Short:
            self._shortPrice = (self._shortPrice * self._shortPos + volume * price) / (self._shortPos + volume)
            self._shortPos += volume
            if isYdPosition:
                self._shortYdPos += volume
            self._shortTdPos = self._shortPos - self._shortYdPos
            self._shortMargin = self.calculate_margin(Direction.Short, self._shortPos, self._shortPrice)
        else:
            self.pos_log(LEVEL_ERROR, 'update_position_by_detail unknown direction {} for {}'\
                         .format(posDetail.direction, posDetail.btSymbol))

    #----------------------------------------------------------------------
    def process_tick_updated(self, lastPrice):
        """行情更新"""
        self.lastPrice = lastPrice
        self.calculate_position_pnl()

        # 计数加1
        self.tickUpdateN += 1

    #----------------------------------------------------------------------
    def get_position_pnl(self, direction=None):
        """获取持仓盈亏"""
        if direction is None:
            return self._longPnl + self._shortPnl
        elif direction == Direction.Long:
            return self._longPnl
        elif direction == Direction.Short:
            return self._shortPnl
        return 0.0

    #----------------------------------------------------------------------
    def get_position_margin(self, direction=None):
        """获取持仓保证金占用"""
        if direction is None:
            return self._longMargin + self._shortMargin
        elif direction == Direction.Long:
            return self._longMargin
        elif direction == Direction.Short:
            return self._shortMargin
        return 0.0

    #----------------------------------------------------------------------
    def calculate_position_pnl(self):
        """计算持仓盈亏"""
        self._longPnl = self._longPos * (self.lastPrice - self._longPrice) * self.multiplier
        self._shortPnl = self._shortPos * (self._shortPrice - self.lastPrice) * self.multiplier

    def calculate_realized_pnl(self, direction, price, volume):
        """计算平仓盈亏"""
        if direction == Direction.Long:
            # 平空仓
            return (self._shortPrice - price) * volume * self.multiplier
        else:
            # 平多仓
            return (price - self._longPrice) * volume * self.multiplier

    def calculate_margin(self, direction, volume, price):
        if direction == Direction.Long:
            return volume * price * self.multiplier * self.marginRate.longMarginRatioByMoney
        else:
            return volume * price * self.multiplier * self.marginRate.shortMarginRatioByMoney

    #----------------------------------------------------------------------
    def calculate_position_price(self, direction):
        """重新计算持仓均价"""
        positionPrice = 0.0
        totalVolume = 0
        for posDetail in self.positionDetails:
            if direction != posDetail.direction:
                continue
            totalVolume += posDetail.volume
            positionPrice += posDetail.positionPrice * posDetail.volume

        if totalVolume > 0:
            positionPrice = positionPrice / totalVolume

        #print("calc_price>> {}.{} volume:{},price:{}".format(self.symbol, direction, totalVolume, positionPrice))

        return positionPrice

    def close_position_detail_data(self, trade):
        """平仓时处理明细数据，返回平仓盈亏和原始占用的保证金"""
        if trade.offset == OFFSET_OPEN:
            return

        margin = 0.0
        realizedPnl = 0.0
        volume = trade.volume
        removes = []
        for posDetail in self.positionDetails:
            if trade.direction == posDetail.direction:
                continue

            # 平今、平昨
            if trade.offset == OFFSET_CLOSETODAY and posDetail.positionDate == POSITION_DATE_YESTERDAY:
                continue

            if volume < posDetail.volume:
                closedVolume = volume
                posDetail.volume -= volume
                volume = 0
            else:
                closedVolume = posDetail.volume
                volume -= posDetail.volume
                removes.append(posDetail)

            # 保证金
            margin += posDetail.margin

            # 计算平仓盈亏
            if posDetail.direction == Direction.Long:
                realizedPnl += (trade.price - posDetail.positionPrice) *\
                    closedVolume * self.multiplier
            else:
                realizedPnl += (posDetail.positionPrice - trade.price) * closedVolume * self.multiplier

            if volume <= 0:
                break

        #print("close_detail: volume:{}, rpnl:{}".format(trade.volume, realizedPnl))

        # 从明细队列中删除
        for _removePos in removes:
            self.pos_log(LEVEL_DEBUG, "remove_pos_detail: {}".format(_removePos))
            self.positionDetails.remove(_removePos)

        return realizedPnl, margin

    #----------------------------------------------------------------------
    def to_dict(self):
        d = {
            'symbol' : self.symbol,
            'btSymbol' : self.btSymbol,
            'multiplier' : self.multiplier,
            'priceTick' : self.priceTick,
            'longPos' : self._longPos,
            'longPrice' : self._longPrice,
            'longPnl' : self._longPnl,
            'longMargin' : self._longMargin,
            'longFrozen' : self._longPosFrozen,
            'longYdFrozen' : self._longYdFrozen,
            'longTdFrozen' : self._longTdFrozen,
            'shortPos' : self._shortPos,
            'shortPrice' : self._shortPrice,
            'shortPnl' : self._shortPnl,
            'shortMargin' : self._shortMargin,
            'shortFrozen' : self._shortPosFrozen,
            'shortYdFrozen' : self._shortYdFrozen,
            'shortTdFrozen' : self._shortTdFrozen,
            'lastPrice' : self.lastPrice,
            'tradingDay' : self.tradingDay
        }
        return d

    #----------------------------------------------------------------------
    def pos_log(self, level, content):
        """position异步日志"""
        if log:
            log.async_log(level, self.logPrefix + content)

    def pos_str(self):
        """返回简单持仓字符串"""
        if self._longPos > 0 and self._shortPos > 0:
            return "longPos:{},longPrice:{},shortPos:{},shortPrice:{}".format(self._longPos, self._longPrice, self._shortPos, self._shortPrice)
        elif self._longPos > 0:
            return "longPos:{},longPrice:{}".format(self._longPos, self._longPrice)
        elif self._shortPos > 0:
            return "shortPos:{},shortPrice:{}".format(self._shortPos, self._shortPrice)
        else:
            return "pos:0"

    #----------------------------------------------------------------------
    def _make_position_detail_data(self, trade, margin):
        posDetail = BtPositionDetailData()
        posDetail.gatewayName = trade.gatewayName
        posDetail.accountID = trade.accountID
        posDetail.brokerID = trade.brokerID

        posDetail.symbol = trade.symbol
        posDetail.exchange = trade.exchange
        posDetail.btSymbol = trade.btSymbol
        posDetail.direction = trade.direction
        posDetail.volume = trade.volume
        posDetail.tradingDay = trade.tradingDay
        posDetail.tradeID = trade.tradeID
        posDetail.btTradeID = '.'.join([trade.exchange, trade.tradeID])
        posDetail.openDate = trade.tradingDay   # not tradeDate
        posDetail.openPrice = trade.price
        posDetail.margin = margin
        posDetail.btPositionName = '.'.join([posDetail.btSymbol, posDetail.direction])
        posDetail.userID = trade.userID
        posDetail.positionDate = POSITION_DATE_TODAY
        posDetail.positionPrice = trade.price
        posDetail.multiplier = self.multiplier
        posDetail.priceTick = self.priceTick
        return posDetail

    def _conv_position_common_field(self, posData):
        posData.accountID = self.accountID
        posData.brokerID = self.brokerID
        posData.symbol = self.symbol
        posData.exchange = self.exchange
        posData.btSymbol = self.btSymbol
        posData.tradingDay = self.tradingDay
        posData.multiplier = self.multiplier
        posData.priceTick = self.priceTick
        posData.lastPrice = self.lastPrice

    def get_position_long(self):
        """多头转为BtPositionData持仓"""
        #if self.longPos == 0:
        #    return None

        posData = BtPositionData()
        self._conv_position_common_field(posData)

        posData.direction = Direction.Long
        posData.position = self._longPos
        posData.frozen = self._longPosFrozen
        posData.price = round(self._longPrice, self.decimal)
        posData.ydPosition = self._longYdPos
        posData.positionPnl = self._longPnl
        posData.useMargin = round(self._longMargin, self.decimal)
        posData.commission = 0.0
        posData.updateTime = self._longUpdateTime

        posData.btPositionName = '.'.join([posData.btSymbol, posData.direction])
        return posData

    def get_position_short(self):
        """空头转为BtPositionData持仓"""
        #if self.shortPos == 0:
        #    return None

        posData = BtPositionData()
        self._conv_position_common_field(posData)

        posData.direction = Direction.Short
        posData.position = self._shortPos
        posData.frozen = self._shortPosFrozen
        posData.price = round(self._shortPrice, self.decimal)
        posData.ydPosition = self._shortYdPos
        posData.positionPnl = self._shortPnl
        posData.useMargin = round(self._shortMargin, self.decimal)
        posData.commission = 0.0
        posData.updateTime = self._shortUpdateTime

        posData.btPositionName = '.'.join([posData.btSymbol, posData.direction])
        return posData
