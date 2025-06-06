
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from aiogram import Bot, Dispatcher
from datetime import datetime

TELEGRAM_TOKEN = '7793423878:AAFW-OTxq_Jew-122scLIV-hMLKN1PDCxdI'
CHANNEL_ID = -1002646802077

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

PAIRS = ["EURUSD=X", "USDJPY=X", "EURCHF=X", "AUDCAD=X", "CADJPY=X", "AUDCHF=X"]

async def main_loop():
    while True:
        await bot.send_message(CHANNEL_ID, "✅ البوت يعمل بشكل سليم! (اختبار)")
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main_loop())
