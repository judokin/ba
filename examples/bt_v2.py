#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
import backtrader as bt
import pandas as pd
import numpy as np
import datetime
import mplfinance as mpf

# 配置日志
config_logging(logging, logging.DEBUG)

# 创建 Binance Spot 客户端
spot_client = Client(base_url="https://testnet.binance.vision")

# 获取最近10天的K线数据
symbol = "XRPUSDT"
interval = "15m"
end_time = int(datetime.datetime.now().timestamp() * 1000)  # 当前时间的毫秒时间戳
start_time = end_time - 10 * 24 * 60 * 60 * 1000  # 10天前的毫秒时间戳

# 获取K线数据
klines = spot_client.klines(symbol, interval, startTime=start_time, endTime=end_time)

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
        self.green_candle_count = 0
        self.trades = []
        self.trade_id = 0
        self.take_profit = 0.005  # 0.5% 收益
        self.stop_loss = 0.005   # 0.5% 损失
        self.buy_price = None
        self.buy_amount = 5000  # 每次买入金额

    def next(self):
        # 检查是否连续三根阳线
        if self.data.close[0] > self.data.open[0]:
            self.green_candle_count += 1
        else:
            self.green_candle_count = 0

        # 买入条件：连续三根阳线且没有持仓
        if self.green_candle_count >= 3 and not self.position:
            self.buy_price = self.data.close[0]
            self.size = self.buy_amount / self.buy_price  # 计算买入数量
            self.buy(size=self.size)
            self.trade_id += 1
            self.trades.append({
                "id": self.trade_id,
                "entry_time": self.data.datetime.datetime(0),
                "entry_price": self.buy_price,
                "exit_time": None,
                "exit_price": None,
                "pnl": None
            })
            print(f"买入: 时间={self.data.datetime.datetime(0)}, 价格={self.buy_price}, 数量={self.size}")

        # 卖出条件：止盈或止损
        if self.position and self.buy_price is not None:
            high_price = self.data.high[0]  # 当前K线的最高价
            low_price = self.data.low[0]    # 当前K线的最低价

            # 止盈逻辑：使用最高价计算收益
            if (high_price - self.buy_price) / self.buy_price >= self.take_profit:
                self.sell()
                self.trades[-1]["exit_time"] = self.data.datetime.datetime(0)
                self.trades[-1]["exit_price"] = high_price
                self.trades[-1]["pnl"] = (high_price - self.buy_price) / self.buy_price
                self.green_candle_count = 0
                self.buy_price = None
                print(f"止盈卖出: 时间={self.data.datetime.datetime(0)}, 价格={high_price}")

            # 止损逻辑：使用最低价计算损失
            elif (self.buy_price - low_price) / self.buy_price >= self.stop_loss:
                self.sell()
                self.trades[-1]["exit_time"] = self.data.datetime.datetime(0)
                self.trades[-1]["exit_price"] = low_price
                self.trades[-1]["pnl"] = (low_price - self.buy_price) / self.buy_price
                self.green_candle_count = 0
                self.buy_price = None
                print(f"止损卖出: 时间={self.data.datetime.datetime(0)}, 价格={low_price}")

    def stop(self):
        winning_trades = [trade for trade in self.trades if trade["pnl"] is not None and trade["pnl"] > 0]
        total_trades = len(self.trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        returns = np.array([trade["pnl"] for trade in self.trades if trade["pnl"] is not None])
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0

        with open("result.txt", "w") as f:
            f.write(f"初始资金: {self.broker.startingcash:.2f}\n")
            f.write(f"最终资金: {self.broker.getvalue():.2f}\n")
            f.write(f"总胜率: {win_rate * 100:.2f}%\n")
            f.write(f"夏普率: {sharpe_ratio:.2f}\n")
            f.write("\n交易记录:\n")
            for trade in self.trades:
                f.write(
                    f"交易ID: {trade['id']}, "
                    f"入场时间: {trade['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}, "
                    f"入场价格: {trade['entry_price']:.4f}, "
                    f"出场时间: {trade['exit_time'].strftime('%Y-%m-%d %H:%M:%S') if trade['exit_time'] else 'N/A'}, "
                    f"出场价格: {trade['exit_price'] if trade['exit_price'] else 'N/A'}, "
                    f"收益率: {trade['pnl'] * 100 if trade['pnl'] is not None else 'N/A'}%\n"
                )

# 创建 Backtrader 引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(ThreeGreenCandlesStrategy)
cerebro.adddata(data)
cerebro.broker.set_cash(10000.0)
cerebro.broker.setcommission(commission=0.001)

print("初始资金: %.2f" % cerebro.broker.getvalue())
cerebro.run()
print("最终资金: %.2f" % cerebro.broker.getvalue())

# 提取买卖信号
df['Buy_Signal_Price'] = np.nan
df['Sell_Signal_Price'] = np.nan

for trade in cerebro.runstrats[0][0].trades:
    if trade['entry_time']:
        df.at[trade['entry_time'], 'Buy_Signal_Price'] = trade['entry_price']
    if trade['exit_time']:
        df.at[trade['exit_time'], 'Sell_Signal_Price'] = trade['exit_price']

# 绘制K线图及交易信号
apds = [
    mpf.make_addplot(df['Buy_Signal_Price'], type='scatter', markersize=100, marker='^', color='g'),
    mpf.make_addplot(df['Sell_Signal_Price'], type='scatter', markersize=100, marker='v', color='r')
]

mpf.plot(df, type='candle', style='charles', volume=True, addplot=apds, title=f'{symbol} K线图及交易信号', mav=(5, 10, 20))