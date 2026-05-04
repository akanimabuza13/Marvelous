## Marvelous - MetaTrader 5 Forex Trading Bot

A professional-grade forex trading signal bot for **MetaTrader 5** that generates buy/sell signals and executes trades automatically with advanced risk management features.

### ✨ Key Features

- **SMA Crossover Signals**: 50-period and 200-period Simple Moving Average crossovers
- **Spread Filter**: Prevents trading when spreads exceed limit (avoids news events)
- **Trailing Stop Loss**: Automatically protects profits as price moves in your favor
- **Take Profit Levels**: Locks in gains at predefined levels
- **Time Filter**: Only trades during high-liquidity NY session (13:00-21:00 UTC)
- **Live MT5 Integration**: Direct execution on MetaTrader 5 platform
- **Risk Management**: Automatic position sizing and stop-loss management

### 🚀 Installation

#### 1. Install MetaTrader 5
- Download and install MetaTrader 5 from your broker's website
- Create a practice or live trading account
- Keep MT5 running while the bot operates

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Bot Settings
Edit these in `forex_signal_bot.py`:

```python
# MT5 Connection
ACCOUNT = 123456789        # Your MT5 account number
PASSWORD = "your_password" # Your MT5 password
SERVER = "ICMarkets-Demo"  # Your broker's server name

# Trading Settings
INSTRUMENT = "EURUSD"      # Currency pair to trade
POSITION_SIZE = 0.01       # Lot size (0.01 = mini lot)

# Risk Management
MAX_SPREAD_PIPS = 2.0      # Max spread to allow (2 pips)
TRAILING_STOP_PIPS = 10    # Stop loss distance (10 pips)
PROFIT_TAKE_PIPS = 20      # Take profit distance (20 pips)
```

### 📊 How It Works

1. **Signal Generation**: Monitors SMA50/SMA200 crossovers on 1-hour candles
2. **Buy Signal**: When SMA50 crosses above SMA200
3. **Sell Signal**: When SMA50 crosses below SMA200
4. **Risk Control**: 
   - Only trades if spread < MAX_SPREAD_PIPS
   - Only trades during NY session (best liquidity)
   - Every order has stop-loss and take-profit
   - Trailing stop protects profits

### ▶️ Running the Bot

```bash
python forex_signal_bot.py
```

Expected output:
```
============================================================
🤖 MARVELOUS FOREX TRADING BOT (MetaTrader 5)
============================================================
Account: 123456789
Balance: $5000.00
Equity: $5000.00

⚙️  Risk Management Settings:
  • Max Spread: 2.0 pips
  • Trailing Stop: 10 pips
  • Take Profit: 20 pips
  • Position Size: 0.01 lots
  • Trading Hours: 13:00 - 21:00 UTC (NY Session)

[2026-05-04 14:30:45] Iteration #1
Signal: +1 | Price: 1.09456 | Positions: 0
📈 BUY SIGNAL DETECTED
✓ BUY ORDER PLACED | Price: 1.09457 | SL: 1.09357 | TP: 1.09657
```

### 🎯 Configuration Tips

**For Conservative Trading (Low Risk)**
```python
TRAILING_STOP_PIPS = 15      # Larger stop loss
PROFIT_TAKE_PIPS = 30        # Higher profit target
MAX_SPREAD_PIPS = 1.5        # Strict spread filter
```

**For Aggressive Trading (Higher Risk/Reward)**
```python
TRAILING_STOP_PIPS = 5       # Tight stop loss
PROFIT_TAKE_PIPS = 15        # Lower profit target
MAX_SPREAD_PIPS = 3.0        # Relaxed spread filter
```

### 📌 Finding Your Server Name

In MetaTrader 5:
1. Go to **File → Account History**
2. Look at the server name in the column (e.g., "ICMarkets-Demo", "Pepperstone-Demo")
3. Copy the exact server name to `SERVER` variable

### ⚠️ Important Safety Notes

✓ **Start with a PRACTICE/DEMO account first**
✓ Test with small position sizes (0.01 lots)
✓ Monitor the bot regularly, don't leave unattended
✓ Forex trading involves substantial risk of loss
✓ Past performance ≠ future results
✓ Only risk money you can afford to lose

### 🔧 Troubleshooting

**Connection Issues**
```python
# Ensure MT5 is running in the background
# Check Account Number and Password are correct
# Verify Server name matches exactly (case-sensitive)
```

**No Orders Placed**
- Check if spread is too high (check `MAX_SPREAD_PIPS`)
- Verify you're in NY trading hours (13:00-21:00 UTC)
- Ensure symbol is correct for your broker (EURUSD vs EURUSDm)

**ModuleNotFoundError: No module named 'MetaTrader5'**
```bash
pip install --upgrade MetaTrader5
```

### 📈 Performance Tracking

The bot displays:
- Current signal and price
- Number of open positions
- Account balance and equity changes
- Order execution confirmations

Monitor these metrics to track bot performance.

### 📄 License

Educational purposes only. Use at your own risk.

### 🤝 Support

If you encounter issues, check:
1. MT5 is running and logged in
2. Server name is correct
3. Account has sufficient margin
4. Symbol name is correct for your broker
5. Python packages are up to date: `pip install --upgrade -r requirements.txt`
