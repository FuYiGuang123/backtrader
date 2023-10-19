import backtrader as bt
import datetime
import pandas as pd
from io import StringIO


data_text = """datetime,open,high,low,close,volume,K线状态,品种名称,品种代码,品种周期,MACD_信号,MACD_diff,MACD_dea,MACD_macd
2023-07-24,18.64 ,19.13 ,17.67 ,18.86 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-0.82 ,-1.10 ,0.57 
2023-07-31,18.86 ,19.07 ,17.72 ,17.85 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-0.82 ,-1.04 ,0.45 
2023-08-07,17.85 ,18.14 ,17.19 ,17.64 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-0.83 ,-1.00 ,0.34 
2023-08-14,17.64 ,17.78 ,13.27 ,15.44 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,-1,-1.01 ,-1.00 ,-0.01 
2023-08-21,15.44 ,16.25 ,14.89 ,16.00 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.09 ,-1.02 ,-0.14 
2023-08-28,16.00 ,17.19 ,15.11 ,15.40 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.19 ,-1.05 ,-0.27 
2023-09-04,15.40 ,15.69 ,14.49 ,15.00 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.29 ,-1.10 ,-0.37 
2023-09-11,15.00 ,15.97 ,14.41 ,15.53 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.30 ,-1.14 ,-0.32 
2023-09-18,15.53 ,16.03 ,15.05 ,15.25 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.32 ,-1.18 ,-0.29 
2023-09-25,15.25 ,16.85 ,14.82 ,16.45 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.23 ,-1.19 ,-0.09 
2023-10-2,16.45 ,16.89 ,15.15 ,15.53 ,0,1,ETC-USDT-SWAP,ETC-USDT-SWAP,1W,0,-1.22 ,-1.19 ,-0.05 """





def create_dynamic_data_class(data):
    # 获取data的列名
    columns = data.columns.tolist()

    # 动态创建新的lines和params
    new_lines = tuple(columns)
    new_params = tuple((col, -1) for col in columns)
    print("new_lines",new_lines)
    print("new_params",new_params)
    # 创建一个新的类，继承自PandasData，并动态添加lines和params
    DynamicPandasData = type('DynamicPandasData', (bt.feeds.PandasData,), {
        'lines': new_lines,
        'params': new_params
    })
    print("DynamicPandasData",DynamicPandasData)


    return DynamicPandasData


# 回测策略
class TestStrategy(bt.Strategy):
    '''选股策略'''
    params = (('maperiod', 15),
              ('printlog', False),)

    def __init__(self):
        pass

    def next(self):
        dt = self.datas[0].datetime.date(0)  # 获取当前的回测时间点
        print( dt,self.datas[0].品种名称[0])
        
        # 交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')



    def notify_order(self, order):
        pass
    
    
def main():
    # 使用pandas的read_csv函数将文本数据转换为DataFrame
    pd_data = pd.read_csv(StringIO(data_text),parse_dates=['datetime'])
    pd_data = pd_data.set_index('datetime')
    # 打印DataFrame
    print(pd_data)
        
    # 实例化 cerebro
    cerebro = bt.Cerebro()      # 创建Cerebro引擎实例
    cerebro.broker.set_cash(100000.00)  # 设置初始资金为100000
    cerebro.broker.setcommission(commission=0.0003)
    cerebro = bt.Cerebro(stdstats=False)     # 创建新的Cerebro引擎实例
    cerebro.addobserver(bt.observers.Trades)  # 添加交易观察者
    cerebro.addobserver(bt.observers.BuySell)  # 添加买卖观察者
    cerebro.addobserver(bt.observers.Value)   # 添加价值观察者
    
    开始时间 = datetime.datetime.fromtimestamp(pd_data.index[0].timestamp())
    结束时间 = datetime.datetime.fromtimestamp(pd_data.index[-1].timestamp())
    # 开始时间 = datetime.datetime.fromtimestamp(pd_data['datetime'].iloc[0].timestamp())
    # 结束时间 = datetime.datetime.fromtimestamp(pd_data['datetime'].iloc[-1].timestamp())
    
    
        # 动态构建参数字典
    params = {
        'dataname': pd_data,
        'fromdate': 开始时间,
        'todate':  结束时间,
        'timeframe': bt.TimeFrame.Weeks,
        'compression': 1
    }

    for col in pd_data.columns:
        params[col] = col

    # 动态创建数据类
    DynamicDataClass = create_dynamic_data_class(pd_data)
    datafeed = DynamicDataClass(**params)

    # datafeed = bt.feeds.PandasData(dataname=pd_data, fromdate=开始时间,todate=结束时间)# 导入数据
    cerebro.adddata(datafeed)
    
    cerebro.addstrategy(TestStrategy, printlog=True)
    
    
    cerebro.run()
    


if __name__ == "__main__":
    main()
