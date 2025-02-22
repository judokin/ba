#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
from examples.utils.prepare_env import get_api_key

config_logging(logging, logging.DEBUG)

api_key, api_secret = get_api_key()

client = Client(api_key, api_secret)

# 获取当前时间戳（毫秒）
current_time_ms = int(time.time() * 1000)

# 设置 startTime 和 endTime
start_time = current_time_ms - 3600 * 1000  # 1 小时前

try:
    response = client.pay_history(startTimestamp=1637186702000, limit=50)
    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
