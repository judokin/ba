#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
from examples.utils.prepare_env import get_api_key

config_logging(logging, logging.DEBUG)

api_key, api_secret = get_api_key()

params = {
    "symbol": "XRPUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "FOK",
    "quantity": 4,
    "price": 3.08,
}

client = Client(api_key, api_secret)

try:
    response = client.new_order(**params)
    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
