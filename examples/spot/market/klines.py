#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

config_logging(logging, logging.DEBUG)

spot_client = Client(base_url="https://testnet.binance.vision")
'''
{
  "id": "1dbbeb56-8eea-466a-8f6e-86bdcfa2fc0b",
  "status": 200,
  "result": [
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
  ],
  "rateLimits": [
    {
      "rateLimitType": "REQUEST_WEIGHT",
      "interval": "MINUTE",
      "intervalNum": 1,
      "limit": 6000,
      "count": 2
    }
  ]
}
'''

logging.info(spot_client.klines("XRPUSDT", "15m"))
