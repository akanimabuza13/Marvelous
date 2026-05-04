import MetaTrader5 as mt5
import ta
import pandas as pd
import time
from datetime import datetime
import pytz

# MT5 Connection Parameters
MT5_PATH = None  # Auto-detect, or specify path like "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
ACCOUNT = None   # Your MT5 account number (if None, uses default)
PASSWORD = ""    # Your MT5 password
SERVER = "ICMarkets-Demo"  # Change to your broker's server

# Trading Configuration
INSTRUMENT = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1  # 1-hour candles
POSITION_SIZE = 0.01  # Lot size (0.01 = 1000 units mini lot)

# Risk Management Features
MAX_SPREAD_PIPS = 2.0      # Max spread to trade (2 pips)
TRAILING_STOP_PIPS = 10    # Trailing stop loss in pips
PROFIT_TAKE_PIPS = 20      # Take profit in pips
NY_SESSION_START = 13      # 1 PM UTC
NY_SESSION_END = 21        # 9 PM UTC

# SMA Parameters
SMA_FAST = 50
SMA_SLOW = 200
LOOKBACK_BARS = 250  # Get enough data for both SMAs

# Initialize MT5
def init_mt5():
    """Initialize MetaTrader5 connection"""
    if not mt5.initialize(path=MT5_PATH, login=ACCOUNT, password=PASSWORD, server=SERVER):
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        return False
    print("✓ MT5 initialized successfully")
    return True

def shutdown_mt5():
    """Safely shutdown MT5"""
    mt5.shutdown()
    print("MT5 connection closed")

def get_account_info():
    """Get account information"""
    info = mt5.account_info()
    if info is None:
        print(f"Failed to get account info: {mt5.last_error()}")
        return None
    return info

def get_symbol_info(symbol=INSTRUMENT):
    """Get symbol information (spread, digits, etc.)"""
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"Symbol {symbol} not found: {mt5.last_error()}")
        return None
    return info

def get_current_spread(symbol=INSTRUMENT):
    """Calculate current spread in pips"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick: {mt5.last_error()}")
        return None
    
    spread_pips = (tick.ask - tick.bid) / mt5.symbol_info(symbol).point
    return spread_pips, tick.ask, tick.bid

def get_historical_data(symbol=INSTRUMENT, timeframe=TIMEFRAME, bars=LOOKBACK_BARS):
    """Fetch historical candlestick data"""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def generate_signals(symbol=INSTRUMENT):
    """Generate buy/sell signals using SMA crossover"""
    data = get_historical_data(symbol)
    if data is None or len(data) < SMA_SLOW:
        return None, None
    
    # Calculate SMAs
    data['SMA50'] = ta.trend.sma_indicator(data['close'], window=SMA_FAST)
    data['SMA200'] = ta.trend.sma_indicator(data['close'], window=SMA_SLOW)
    
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    current_price = latest['close']
    
    signal = 0
    # Buy: SMA50 crosses above SMA200
    if prev['SMA50'] < prev['SMA200'] and latest['SMA50'] > latest['SMA200']:
        signal = 1
    # Sell: SMA50 crosses below SMA200
    elif prev['SMA50'] > prev['SMA200'] and latest['SMA50'] < latest['SMA200']:
        signal = -1
    
    return signal, current_price

def is_trading_hours():
    """Check if current time is within NY session (high liquidity)"""
    utc_time = datetime.now(pytz.UTC)
    current_hour = utc_time.hour
    
    # NY session: 13:00 - 21:00 UTC
    if NY_SESSION_START <= current_hour < NY_SESSION_END:
        return True
    return False

def is_spread_ok(symbol=INSTRUMENT):
    """Check if spread is within acceptable limits"""
    spread_info = get_current_spread(symbol)
    if spread_info is None:
        return False
    
    spread_pips, ask, bid = spread_info
    if spread_pips > MAX_SPREAD_PIPS:
        print(f"⚠️  Spread too high: {spread_pips:.2f} pips (max: {MAX_SPREAD_PIPS})")
        return False
    return True

def get_open_positions(symbol=INSTRUMENT):
    """Get all open positions for the symbol"""
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return []
    return list(positions)

def close_all_positions(symbol=INSTRUMENT):
    """Close all open positions for the symbol"""
    positions = get_open_positions(symbol)
    if not positions:
        return True
    
    for pos in positions:
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": pos.ticket,
            "deviation": 20,
            "magic": 999,
            "comment": "close_position"
        }
        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ Failed to close position {pos.ticket}: {result.comment}")
            return False
        print(f"✓ Closed position {pos.ticket}")
    return True

def place_buy_order(symbol=INSTRUMENT, volume=POSITION_SIZE):
    """Place a buy order with trailing stop and take profit"""
    if not is_spread_ok(symbol):
        print("❌ Spread too high, order rejected")
        return False
    
    spread_info = get_current_spread(symbol)
    ask_price = spread_info[1]
    point = mt5.symbol_info(symbol).point
    
    # Calculate stop loss and take profit
    stop_loss = ask_price - (TRAILING_STOP_PIPS * point)
    take_profit = ask_price + (PROFIT_TAKE_PIPS * point)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": ask_price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 123456,
        "comment": "buy_signal"
    }
    
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✓ BUY ORDER PLACED | Price: {ask_price:.5f} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
        return True
    else:
        print(f"❌ Buy order failed: {result.comment}")
        return False

def place_sell_order(symbol=INSTRUMENT, volume=POSITION_SIZE):
    """Place a sell order with trailing stop and take profit"""
    if not is_spread_ok(symbol):
        print("❌ Spread too high, order rejected")
        return False
    
    spread_info = get_current_spread(symbol)
    bid_price = spread_info[2]
    point = mt5.symbol_info(symbol).point
    
    # Calculate stop loss and take profit
    stop_loss = bid_price + (TRAILING_STOP_PIPS * point)
    take_profit = bid_price - (PROFIT_TAKE_PIPS * point)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": bid_price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 123456,
        "comment": "sell_signal"
    }
    
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✓ SELL ORDER PLACED | Price: {bid_price:.5f} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
        return True
    else:
        print(f"❌ Sell order failed: {result.comment}")
        return False

def trading_bot():
    """Main trading bot loop"""
    if not init_mt5():
        return
    
    print("=" * 60)
    print("🤖 MARVELOUS FOREX TRADING BOT (MetaTrader 5)")
    print("=" * 60)
    
    account = get_account_info()
    if account:
        print(f"Account: {account.login}")
        print(f"Balance: ${account.balance:.2f}")
        print(f"Equity: ${account.equity:.2f}")
    
    symbol_info = get_symbol_info(INSTRUMENT)
    if symbol_info:
        print(f"Symbol: {INSTRUMENT} | Digits: {symbol_info.digits}")
    
    print("\n⚙️  Risk Management Settings:")
    print(f"  • Max Spread: {MAX_SPREAD_PIPS} pips")
    print(f"  • Trailing Stop: {TRAILING_STOP_PIPS} pips")
    print(f"  • Take Profit: {PROFIT_TAKE_PIPS} pips")
    print(f"  • Position Size: {POSITION_SIZE} lots")
    print(f"  • Trading Hours: {NY_SESSION_START}:00 - {NY_SESSION_END}:00 UTC (NY Session)")
    print("\n" + "=" * 60 + "\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Iteration #{iteration}")
            
            # Check if within trading hours
            if not is_trading_hours():
                print(f"⏰ Outside NY session. Waiting...")
                time.sleep(300)  # Check every 5 minutes
                continue
            
            # Get signal
            signal, price = generate_signals(INSTRUMENT)
            if signal is None:
                print("❌ Failed to generate signal")
                time.sleep(60)
                continue
            
            # Get current positions
            positions = get_open_positions(INSTRUMENT)
            has_position = len(positions) > 0
            
            print(f"Signal: {signal:+d} | Price: {price:.5f} | Positions: {len(positions)}")
            
            # Execute trades based on signals
            if signal == 1 and not has_position:  # BUY SIGNAL
                print("📈 BUY SIGNAL DETECTED")
                place_buy_order(INSTRUMENT, POSITION_SIZE)
            
            elif signal == -1 and not has_position:  # SELL SIGNAL
                print("📉 SELL SIGNAL DETECTED")
                place_sell_order(INSTRUMENT, POSITION_SIZE)
            
            # Check account equity
            account = get_account_info()
            if account:
                print(f"Current Equity: ${account.equity:.2f}")
            
            print("-" * 60 + "\n")
            time.sleep(3600)  # Check every hour
            
    except KeyboardInterrupt:
        print("\n⛔ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        shutdown_mt5()

if __name__ == "__main__":
    trading_bot()
