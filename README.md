# Marvelous

A forex trading signal bot that generates buy/sell signals and executes trades automatically using OANDA API.

## Features

- Generates trading signals based on 50-period and 200-period Simple Moving Average crossovers
- Integrates with OANDA for live forex trading
- Tracks balance and profits
- Automatic order placement on signals
- Simulated withdrawal notification when profit threshold is reached

## Setup

1. Create an OANDA account (practice or live) at https://www.oanda.com/
2. Get your Account ID and Access Token from the OANDA dashboard
3. Set environment variables:
   ```
   export OANDA_ACCOUNT_ID="your_account_id"
   export OANDA_ACCESS_TOKEN="your_access_token"
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the bot:
```
python forex_signal_bot.py
```

The bot will run continuously, checking for signals every hour and placing orders accordingly.

## Trading Logic

- **Buy Signal**: When SMA50 crosses above SMA200
- **Sell Signal**: When SMA50 crosses below SMA200
- Uses 1000 units (0.01 lots) per trade
- Monitors balance and alerts for profits over $100

## Withdrawal

The bot prints a message when profits exceed $100. For actual withdrawal:
- Use OANDA's web interface to transfer funds to your bank
- Or implement API calls for account transfers (see OANDA API docs)

## Disclaimer

This bot uses real money trading. Forex trading involves significant risk of loss. Test with a practice account first. The bot is for educational purposes only. Past performance does not guarantee future results. Use at your own risk.