#!/usr/bin/env python
import sys
import logging
import time
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
from examples.utils.prepare_env import get_api_key

config_logging(logging, logging.DEBUG)

api_key, api_secret = get_api_key()

client = Client(api_key, api_secret)




def run():
    ticker_price_resp = client.ticker_price("XRPUSDT")
    params = {
        "symbol": "XRPUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "FOK",
        "quantity": 4,
        "price": ticker_price_resp['price'],
    }

    # 获取账户余额
    account_info = client.account()
    balances = account_info['balances']
    # 获取 USDT 余额
    usdt_balance = next(filter(lambda x: x['asset'] == 'USDT', balances))['free']
    usdt_balance = float(usdt_balance)
    #import pdb; pdb.set_trace()
    print(usdt_balance)
    if usdt_balance < 12:
        print("余额不足!!")
        sys.exit(0) 

    if float(params['price']) >= 3:
        print("大于目标价，当前价格为:", params['price'])
        sys.exit(0)

    # 获取当前时间戳（毫秒）
    current_time_ms = int(time.time() * 1000)

    # 设置 startTime 和 endTime
    start_time = current_time_ms - 3600 * 1000  # 1 小时前
    end_time = current_time_ms  # 当前时间
    try:
        response = client.new_order(**params)
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
if __name__ == "__main__":
    run()