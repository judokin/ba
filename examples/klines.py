#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
import mplfinance as mpf
import pandas as pd

# 配置日志
config_logging(logging, logging.DEBUG)

# 创建 Binance Spot 客户端
spot_client = Client(base_url="https://testnet.binance.vision")

# 获取K线数据
symbol = "XRPUSDT"
interval = "15m"
klines = spot_client.klines(symbol, interval)

'''
    [
      1655971200000,      // 这根K线的起始时间
      "0.01086000",       // 这根K线期间第一笔成交价
      "0.01086600",       // 这根K线期间最高成交价
      "0.01083600",       // 这根K线期间最低成交价
      "0.01083800",       // 这根K线期间末一笔成交价
      "2290.53800000",    // 这根K线期间成交量
      1655974799999,      // 这根K线的结束时间
      "24.85074442",      // 这根K线期间成交额
      2283,               // 这根K线期间成交笔数
      "1171.64000000",    // 主动买入的成交量
      "12.71225884",      // 主动买入的成交额
      "0"                 // 忽略此参数
    ]
'''
# 将K线数据转换为 DataFrame
columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"]
df = pd.DataFrame(klines, columns=columns)

# 转换数据类型
df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
df["Close Time"] = pd.to_datetime(df["Close Time"], unit="ms")
df["Open"] = df["Open"].astype(float)
df["High"] = df["High"].astype(float)
df["Low"] = df["Low"].astype(float)
df["Close"] = df["Close"].astype(float)
df["Volume"] = df["Volume"].astype(float)

# 设置时间为索引
df.set_index("Open Time", inplace=True)

# 绘制K线图
mpf.plot(df, type="candle", volume=True, style="charles", title=f"{symbol} {interval} K线图", ylabel="Price", ylabel_lower="Volume")