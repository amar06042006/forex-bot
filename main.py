
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

def calculate_indicators(df):
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def analyze(pair):
    df = yf.download(pair, interval="1m", period="1d", auto_adjust=True)
    if df.empty or len(df) < 30:
        return None
    df = calculate_indicators(df)
    latest = df.iloc[-1]

    if pd.isna(latest[['EMA9', 'EMA21', 'MACD', 'Signal', 'RSI']]).any().any():
        return None

    ema9 = latest['EMA9']
    ema21 = latest['EMA21']
    macd = latest['MACD']
    signal = latest['Signal']
    rsi = latest['RSI']
    price = latest['Close']

    buy = ema9 > ema21 and macd > signal and rsi > 50
    sell = ema9 < ema21 and macd < signal and rsi < 50
    trade_signal = "BUY" if buy else "SELL" if sell else None

    if trade_signal:
        confidence = round(
            abs(macd - signal) * 100 +
            abs(ema9 - ema21) * 50 +
            abs(rsi - 50), 2
        )
        score = min(confidence / 3, 99.9)
        if score < 70:
            return None
        return {
            'pair': pair.replace("=X", ""),
            'signal': trade_signal,
            'price': round(price, 5),
            'confidence': score,
            'time': datetime.now().strftime("%H:%M:%S")
        }
    return None

async def send_signal_and_result():
    results = []
    for pair in PAIRS:
        result = analyze(pair)
        if result:
            results.append(result)
    if results:
        best = sorted(results, key=lambda x: x['confidence'], reverse=True)[0]
        entry_time = (datetime.now() + pd.Timedelta(minutes=1)).strftime("%H:%M:%S")
        msg = f"📢 إشارة تداول بعد دقيقة\nزوج: {best['pair']}\nالاتجاه: {best['signal']}\nالسعر الحالي: {best['price']}\nالثقة: {best['confidence']}%\nوقت الدخول: {entry_time}\nمدة الصفقة: 1 دقيقة"
        await bot.send_message(CHANNEL_ID, msg)

        await asyncio.sleep(60)
        await asyncio.sleep(60)

        df_after = yf.download(best['pair'] + "=X", interval="1m", period="5m", auto_adjust=True)
        if df_after.empty or len(df_after) < 2:
            await bot.send_message(CHANNEL_ID, f"❓ لم يتمكن البوت من تحديد نتيجة الصفقة.")
            return
        price_now = df_after.iloc[-1]['Close']
        result = "✅ WIN" if (best['signal'] == "BUY" and price_now > best['price']) or (best['signal'] == "SELL" and price_now < best['price']) else "❌ LOSS"
        await bot.send_message(CHANNEL_ID, f"📊 نتيجة الصفقة على {best['pair']}: {result} (من {best['price']} إلى {round(price_now, 5)})")

async def main_loop():
    while True:
        try:
            await send_signal_and_result()
        except Exception as e:
            await bot.send_message(CHANNEL_ID, f"⚠️ خطأ في البوت: {e}")
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main_loop())
