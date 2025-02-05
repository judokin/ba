#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
import backtrader as bt
import pandas as pd
import numpy as np
import datetime

# 配置日志
config_logging(logging, logging.DEBUG)

# 创建 Binance Spot 客户端
spot_client = Client(base_url="https://testnet.binance.vision")

# 获取最近30天的K线数据
symbol = "XRPUSDT"
interval = "15m"
end_time = int(datetime.datetime.now().timestamp() * 1000)  # 当前时间的毫秒时间戳
start_time = end_time - 10 * 24 * 60 * 60 * 1000  # 30天前的毫秒时间戳

# 获取K线数据
#klines = spot_client.klines(symbol, interval, startTime=start_time, endTime=end_time)
klines = spot_client.klines(symbol, interval)

# 将K线数据转换为 DataFrame
columns = [
    "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
    "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume",
    "Taker Buy Quote Asset Volume", "Ignore"
]
df = pd.DataFrame(klines, columns=columns)

# 转换数据类型
df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
df["Close"] = df["Close"].astype(float)
df["High"] = df["High"].astype(float)
df["Low"] = df["Low"].astype(float)
df["Open"] = df["Open"].astype(float)
df["Volume"] = df["Volume"].astype(float)

# 设置时间为索引
df.set_index("Open Time", inplace=True)

# 将数据转换为 Backtrader 的格式
data = bt.feeds.PandasData(dataname=df)

# 定义策略
class ThreeGreenCandlesStrategy(bt.Strategy):
    def __init__(self):
        # 用于跟踪连续阳线的计数器
        self.green_candle_count = 0
        # 用于记录交易
        self.trades = []
        self.trade_id = 0

    def next(self):
        # 如果当前是阳线（收盘价 > 开盘价）
        if self.data.close[0] > self.data.open[0]:
            self.green_candle_count += 1
        else:
            self.green_candle_count = 0  # 重置计数器

        # 如果连续三个阳线且未持仓，则全仓买入
        if self.green_candle_count >= 3 and not self.position:
            self.buy()  # 全仓买入
            self.trade_id += 1
            self.trades.append({
                "id": self.trade_id,
                "entry_time": self.data.datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S"),
                "entry_price": self.data.close[0],
                "exit_time": None,
                "exit_price": None,
                "pnl": None
            })

        # 如果已经持仓且到了第四根K线，则卖出
        if self.position and len(self.trades) > 0 and self.trades[-1]["exit_time"] is None:
            self.sell()  # 卖出
            self.trades[-1]["exit_time"] = self.data.datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S")
            self.trades[-1]["exit_price"] = self.data.close[0]
            self.trades[-1]["pnl"] = (self.data.close[0] - self.trades[-1]["entry_price"]) / self.trades[-1]["entry_price"]
            self.green_candle_count = 0  # 重置计数器

    def stop(self):
        # 计算总胜率
        winning_trades = [trade for trade in self.trades if trade["pnl"] is not None and trade["pnl"] > 0]
        total_trades = len(self.trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        # 计算夏普率
        returns = np.array([trade["pnl"] for trade in self.trades if trade["pnl"] is not None])
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0

        # 输出结果到文件
        with open("result.txt", "w") as f:
            f.write(f"初始资金: {self.broker.startingcash:.2f}\n")
            f.write(f"最终资金: {self.broker.getvalue():.2f}\n")
            f.write(f"总胜率: {win_rate * 100:.2f}%\n")
            f.write(f"夏普率: {sharpe_ratio:.2f}\n")
            f.write("\n交易记录:\n")
            for trade in self.trades:
                f.write(
                    f"交易ID: {trade['id']}, "
                    f"入场时间: {trade['entry_time']}, "
                    f"入场价格: {trade['entry_price']:.4f}, "
                    f"出场时间: {trade['exit_time'] if trade['exit_time'] is not None else 'N/A'}, "
                    f"出场价格: {trade['exit_price'] if trade['exit_price'] is not None else 'N/A'}, "
                    f"收益率: {trade['pnl'] * 100 if trade['pnl'] is not None else 'N/A'}%\n"
                )

# 创建 Backtrader 引擎
cerebro = bt.Cerebro()

# 添加策略
cerebro.addstrategy(ThreeGreenCandlesStrategy)

# 添加数据
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.set_cash(10000.0)

# 设置交易手续费（假设为 0.1%）
cerebro.broker.setcommission(commission=0.001)

# 运行回测
print("初始资金: %.2f" % cerebro.broker.getvalue())
cerebro.run()
print("最终资金: %.2f" % cerebro.broker.getvalue())

# 绘制回测结果
cerebro.plot()