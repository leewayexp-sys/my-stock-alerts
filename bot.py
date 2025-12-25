import yfinance as yf
import pandas_ta as ta
import requests
import os

# Get your hidden keys from GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# List your stocks here
STOCKS = ["AAL", "PYPL"] 

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(url)

for stock in STOCKS:
    try:
        # 1. Download data (using the newest format fix)
        df = yf.download(stock, period="1mo", interval="1d", auto_adjust=True)
        
        # 2. Safety Check: Is the data empty?
        if df.empty:
            print(f"Skipping {stock}: No data found.")
            continue

        # 3. Calculate RSI
        # We use .squeeze() to handle the new Yahoo Finance multi-column format
        rsi_series = ta.rsi(df['Close'].squeeze(), length=14)

        # 4. Safety Check: Did RSI calculation work?
        if rsi_series is None or rsi_series.empty:
            print(f"Skipping {stock}: Could not calculate RSI.")
            continue

        current_rsi = rsi_series.iloc[-1]
        print(f"{stock}: RSI is {current_rsi:.22f}")

        # 5. Send Alerts
        if current_rsi <= 30:
            send_alert(f"🟢 {stock} is Oversold! RSI: {round(float(current_rsi), 2)}")
        elif current_rsi >= 70:
            send_alert(f"🔴 {stock} is Overbought! RSI: {round(float(current_rsi), 2)}")

    except Exception as e:
        print(f"Error processing {stock}: {e}")
