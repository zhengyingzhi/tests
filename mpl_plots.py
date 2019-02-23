#### mpl_finance K线 
import talib
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf

def plotcandlestict(instrument,start_date,end_date,sma_n1,sma_n2):
    start_date = start_date
    end_date = end_date
    id_ohlc = 'AShareEODPrices'
    target_fields=['open', 'high', 'low', 'close', 'volume', 'amount', 'adjust_factor']
    origin_fields=['s_dq_adjopen','s_dq_adjhigh','s_dq_adjlow','s_dq_adjclose','s_dq_volume','s_dq_admount','s_dq_adjfactor']
    ohlc_df = DataSource(id_ohlc).read([instrument], start_date=start_date, end_date=end_date,
                                  fields=origin_fields)
    ohlc_df.rename_axis({x:y for x,y in zip(origin_fields,target_fields)},axis=1, inplace=True)

    data=ohlc_df.set_index('date')

    # 计算 10 日和 30 日均线
    #使用talib的时候需要更改数据类型....
    sma_1 = talib.SMA(np.array(data['close'].astype('double')), sma_n1)
    sma_2 = talib.SMA(np.array(data['close'].astype('double')), sma_n2)

    # 创建图像和子图
    fig = plt.figure(figsize=(17, 10))
    ax = fig.add_axes([0,0.2,1,0.5])
    ax2 = fig.add_axes([0,0,1,0.2])

    # k 线
    mpf.candlestick2_ochl(ax, data['open'], data['close'], data['high'], data['low'], 
                          width=0.5, colorup='r', colordown='g', alpha=0.8)

    # 设置横轴坐标
    ax.set_xticks(range(0, len(data.index), 10))
    ax.plot(sma_1, label=str('sma%s'%sma_n1))
    ax.plot(sma_2, label=str('sma%s'%sma_n2))

    # 创建图例
    ax.legend(loc='upper left')

    # 网格
    ax.grid(True)

    # 成交量
    mpf.volume_overlay(ax2, data['open'], data['close'], data['volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
    ax2.set_xticks(range(0, len(data.index), 10))
    ax2.set_xticklabels(data.index.strftime('%Y-%m-%d')[::10], rotation=30)
    ax2.grid(True)

    plt.show() 
    
plotcandlestict('000001.SZ','2017-01-01','2017-11-21',10,20)
