#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from examples.utils.prepare_env import get_api_key

config_logging(logging, logging.DEBUG)

# HMAC authentication with API key and secret
#import pdb;pdb.set_trace()
# my = {"apiKey":"mrbT4DXBL4lvjBPv84hO05E8kNOGZBLgRAYtbx32vXihlSDkYVqi3fDCsCzihymD","secretKey":"8hUb4P3PMXzyjL1DCBmeCcf7NLMZB1jUJ2MZozr2ziLZ8udJ9npxJ3Rzp9XpLbaw","comment":"BTC"}
# api_key, api_secret = [my["apiKey"], my["secretKey"]]
# 替换为您的API密钥和Secret Key
# api_key = 'mrbT4DXBL4lvjBPv84hO05E8kNOGZBLgRAYtbx32vXihlSDkYVqi3fDCsCzihymD'
# api_secret = '8hUb4P3PMXzyjL1DCBmeCcf7NLMZB1jUJ2MZozr2ziLZ8udJ9npxJ3Rzp9XpLbaw'
#client = Client(api_key, api_secret, base_url="https://testnet.binance.vision")
api_key, api_secret = get_api_key()
client = Client(api_key, api_secret)
logging.info(client.account(recvWindow=6000))
import pdb;pdb.set_trace()

# RSA authentication with RSA key
api_key = ""
with open("/Users/john/ssl/private_key.pem", "r") as f:
    private_key = f.read()

client = Client(
    api_key, base_url="https://testnet.binance.vision", private_key=private_key
)
logging.info(client.account())


api_key = ""
with open("/Users/john/ssl/private_key.pem", "r") as f:
    private_key = f.read()

client = Client(
    api_key=api_key,
    base_url="https://testnet.binance.vision",
    private_key=private_key,
    private_key_pass="password",
)
logging.info(client.account())
