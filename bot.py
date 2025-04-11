
import time, datetime, requests
import pandas as pd
import ta
from binance.client import Client
from binance.enums import *
import openai
from telegram import Bot
from config import *

client = Client(API_KEY, API_SECRET)
openai.api_key = OPENAI_KEY
bot = Bot(token=TELEGRAM_TOKEN)

def fetch_data():
    candles = client.get_klines(symbol=SYMBOL, interval='1m', limit=100)
    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['EMA9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['EMA21'] = ta.trend.ema_indicator(df['close'], window=21)
    return df

def get_signal(df):
    if df['EMA9'].iloc[-2] < df['EMA21'].iloc[-2] and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1]:
        return 'buy'
    elif df['EMA9'].iloc[-2] > df['EMA21'].iloc[-2] and df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1]:
        return 'sell'
    return None

def get_account_data():
    account = client.get_account()
    balances = {bal['asset']: float(bal['free']) for bal in account['balances']}
    return balances

def get_open_positions():
    try:
        positions = client.get_open_orders(symbol=SYMBOL)
        return positions
    except:
        return []

def get_price():
    return float(client.get_symbol_ticker(symbol=SYMBOL)['price'])

def ask_ai(signal, balance, price, positions):
    summary = f"Signal: {signal}, Price: {price}, Balance: {balance}, Positions: {positions}"
    prompt = f"Based on this: {summary}, should we execute the trade? YES or NO + reason."
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def execute_trade(order_type):
    if TEST_MODE:
        print(f"[TEST] {order_type.upper()} trade executed.")
        return f"[TEST] {order_type.upper()} trade executed."
    try:
        if order_type == 'buy':
            client.order_market_buy(symbol=SYMBOL, quantity=QUANTITY)
        elif order_type == 'sell':
            client.order_market_sell(symbol=SYMBOL, quantity=QUANTITY)
        return f"Executed {order_type} trade."
    except Exception as e:
        return f"Error: {e}"
