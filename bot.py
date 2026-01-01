import os
import requests
import pandas_ta as ta
import time
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# 1. FETCH KEYS FROM GITHUB ENV
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 2. VALIDATION: Ensure keys are not empty
if not API_KEY or not SECRET_KEY:
    print(f"❌ AUTH ERROR: ALPACA_API_KEY is {'MISSING' if not API_KEY else 'OK'}")
    print(f"❌ AUTH ERROR: ALPACA_SECRET_KEY is {'MISSING' if not SECRET_KEY else 'OK'}")
    exit(1)

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(url)

# Initialize Alpaca Client
client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)

STOCKS = ["AAL", "PYPL"]

print("🚀 Bot Started: Monitoring 1-minute RSI...")

# Loop for 55 minutes (allows GitHub to cycle every hour)
timeout = time.time() + 60*55
while time.time() < timeout:
    for stock in STOCKS:
        try:
            # Fetch last 3 hours of 1-minute bars to calculate 14-period RSI
            request_params = StockBarsRequest(
                symbol_or_symbols=stock,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(hours=3)
            )
            bars = client.get_stock_bars(request_params).df
            
            if bars.empty:
                continue

            # Calculate RSI on 'close' column
            rsi_series = ta.rsi(bars['close'], length=14)
            if rsi_series is None or rsi_series.empty:
                continue

            current_rsi = rsi_series.iloc[-1]
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {stock}: RSI {round(current_rsi, 2)}")

            # Thresholds
            if current_rsi <= 25:
                send_alert(f"🟢 1m OVERSOLD: {stock} | RSI: {round(current_rsi, 2)}")
            elif current_rsi >= 85:
                send_alert(f"🔴 1m OVERBOUGHT: {stock} | RSI: {round(current_rsi, 2)}")

        except Exception as e:
            print(f"⚠️ Error processing {stock}: {e}")

    # Sleep for 60 seconds for the next 1-minute candle
    time.sleep(60)
