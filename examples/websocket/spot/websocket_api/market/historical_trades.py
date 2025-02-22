#!/usr/bin/env python

import logging
import time
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

config_logging(logging, logging.DEBUG)


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)


my_client = SpotWebsocketAPIClient(
    on_message=message_handler, on_close=on_close, time_unit="microsecond"
)


my_client.historical_trades(symbol="BNBBUSD", apiKey="", limit=1)

time.sleep(2)

logging.info("closing ws connection")
my_client.stop()
