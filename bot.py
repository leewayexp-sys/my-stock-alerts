import yfinance as yf
import pandas_ta as ta
import requests
import os

# Get your hidden keys
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# List your stocks here!
STOCKS = ["AAPL", "TSLA", "NVDA", "BTC-USD"] 

def send_alert(msg):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}")

for stock in STOCKS:
    data = yf.download(stock, period="1mo", interval="1d")
    if not data.empty:
        # Calculate RSI
        rsi = ta.rsi(data['Close'], length=14).iloc[-1]
        
        if rsi <= 30:
            send_alert(f"🟢 {stock} is Oversold! RSI is {round(float(rsi), 2)}")
        elif rsi >= 70:
            send_alert(f"🔴 {stock} is Overbought! RSI is {round(float(rsi), 2)}")
