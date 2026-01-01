import os
import requests
import pandas_ta as ta
import time
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# Keys from GitHub Secrets
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

STOCKS = ["AAL", "PYPL"]
client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(url)

# Loop for 55 minutes
timeout = time.time() + 60*55
while time.time() < timeout:
    for stock in STOCKS:
        try:
            # Request real-time 1-minute bars
            request_params = StockBarsRequest(
                symbol_or_symbols=stock,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(hours=3) # Get enough data for RSI
            )
            bars = client.get_stock_bars(request_params).df
            
            # Calculate RSI on the 'close' price
            rsi = ta.rsi(bars['close'], length=14).iloc[-1]
            
            print(f"{stock} 1m RSI: {round(rsi, 2)}")

            if rsi <= 25:
                send_alert(f"🚀 REAL-TIME: {stock} is OVERSOLD! RSI: {round(rsi, 2)}")
            elif rsi >= 75:
                send_alert(f"⚠️ REAL-TIME: {stock} is OVERBOUGHT! RSI: {round(rsi, 2)}")

        except Exception as e:
            print(f"Error on {stock}: {e}")
            
    time.sleep(60) # Wait for the next 1-minute candle
