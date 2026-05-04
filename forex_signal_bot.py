import yfinance as yf
import ta
import pandas as pd
import time
import os
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.endpoints.accounts import AccountSummary, AccountChanges
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.trades as trades

# OANDA credentials (set as environment variables)
accountID = os.getenv('OANDA_ACCOUNT_ID')
access_token = os.getenv('OANDA_ACCESS_TOKEN')
environment = "practice"  # or "live"

api = API(access_token=access_token, environment=environment)

def get_live_price(instrument="EUR_USD"):
    # Get current price
    from oandapyV20.endpoints.pricing import PricingInfo
    params = {"instruments": instrument}
    r = PricingInfo(accountID=accountID, params=params)
    api.request(r)
    return float(r.response['prices'][0]['bids'][0]['price'])

def place_order(instrument="EUR_USD", units=1000, side="buy"):
    data = {
        "order": {
            "units": str(units) if side == "buy" else str(-units),
            "instrument": instrument,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    r = OrderCreate(accountID, data=data)
    try:
        api.request(r)
        return r.response
    except V20Error as e:
        print(f"Order error: {e}")
        return None

def get_balance():
    r = AccountSummary(accountID)
    api.request(r)
    return float(r.response['account']['balance'])

def close_position(instrument="EUR_USD"):
    # Close all positions for the instrument
    data = {"longUnits": "ALL", "shortUnits": "ALL"}
    r = positions.PositionClose(accountID, instrument=instrument, data=data)
    try:
        api.request(r)
        return r.response
    except V20Error as e:
        print(f"Close position error: {e}")
        return None

def generate_signals_live(instrument="EUR_USD", window=50):
    # For live, we need historical data to calculate SMA
    # Use yfinance for simplicity, but in production, use OANDA historical
    ticker = "EURUSD=X"
    data = yf.download(ticker, period="1mo", interval="1h")  # last month hourly
    data.columns = data.columns.droplevel(1)
    data['SMA50'] = ta.trend.sma_indicator(data['Close'], window=window)
    data['SMA200'] = ta.trend.sma_indicator(data['Close'], window=200)
    
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    
    signal = 0
    if prev['SMA50'] < prev['SMA200'] and latest['SMA50'] > latest['SMA200']:
        signal = 1  # Buy
    elif prev['SMA50'] > prev['SMA200'] and latest['SMA50'] < latest['SMA200']:
        signal = -1  # Sell
    
    return signal, latest['Close']

def trading_bot():
    instrument = "EUR_USD"
    position = 0  # 0: no position, 1: long, -1: short
    balance = get_balance()
    print(f"Initial balance: {balance}")
    
    while True:
        signal, price = generate_signals_live(instrument)
        print(f"Signal: {signal}, Price: {price}, Position: {position}")
        
        if signal == 1 and position != 1:
            # Buy
            if position == -1:
                close_position(instrument)
            place_order(instrument, units=1000, side="buy")
            position = 1
            print("Bought")
        elif signal == -1 and position != -1:
            # Sell
            if position == 1:
                close_position(instrument)
            place_order(instrument, units=1000, side="sell")
            position = -1
            print("Sold")
        
        # Check balance
        new_balance = get_balance()
        if new_balance > balance + 100:  # If profit > 100, "withdraw" by printing or something
            print(f"Profit made: {new_balance - balance}. Consider withdrawing.")
            # For automatic withdrawal, you can implement transfer to another account
            # But for demo, just print
        balance = new_balance
        
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    if not accountID or not access_token:
        print("Please set OANDA_ACCOUNT_ID and OANDA_ACCESS_TOKEN environment variables.")
    else:
        trading_bot()