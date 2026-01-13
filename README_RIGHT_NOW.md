# FX Carry Bot - What's Going On Right Now

## 🎯 Project Overview

This is a **real-time stock trading analysis bot** that:
1. Streams live price data from Yahoo Finance
2. Aggregates tick data into time-based candlestick bars (OHLC)
3. Calculates MACD (Moving Average Convergence Divergence) indicators
4. Generates BUY/SELL signals based on MACD crossovers
5. Backtests strategies using historical data

**Current Status**: The bot can stream live data, detect trading signals, and backtest strategies with historical data.

---

## 📁 File Structure & What Each File Does

### **Core Components**

#### `barAggregator.py` - The Data Organizer
- **What it does**: Converts individual price ticks into candlestick bars
- **How**: Groups prices into time buckets (e.g., 5-minute intervals)
- **Output**: OHLC bars (Open, High, Low, Close) with timestamps
- **Key class**: `BarAggregator(interval_seconds=60)`
  - `interval_seconds`: How long each bar represents (60 = 1 minute, 300 = 5 minutes)
  - `update(price, timestamp)`: Feed it prices, it builds bars
  - `bars`: Collection of completed bars (max 500)
  - `current_bar`: The bar currently being built

#### `MACD.py` - The Signal Calculator
- **What it does**: Calculates MACD indicator from price bars
- **How**: Uses exponential moving averages (EMA)
  - Fast EMA (18 periods) - Slow EMA (26 periods) = MACD line
  - 9-period EMA of MACD = Signal line
  - MACD - Signal = Histogram
- **Returns**: `(macd, signal, histogram)` values
- **Why it matters**: MACD crossovers indicate potential buy/sell opportunities

#### `livePull.py` - The Live Trading Monitor ⭐ MAIN FILE
- **What it does**: Real-time market monitoring with live signal detection
- **Key features**:
  - Streams live price data via WebSocket
  - Builds 5-minute bars in real-time
  - Calculates MACD every bar
  - Prints BUY/SELL signals when detected
  - Logs all bars and MACD data to `logs/` directory
- **Configuration**:
  - `ticker_symbol = "EVTV"` - Stock to monitor
  - `interval_seconds=300` - 5-minute bars
  - `SHOULD_PRINT_BARS = False` - Toggle bar printing on/off
- **How to run**: `python3 livePull.py`

#### `TradingBot.py` - The Portfolio Manager (Not Yet Used)
- **What it does**: Manages virtual trading portfolio
- **Features**:
  - Track balance
  - Buy/sell assets
  - Maintain portfolio positions
- **Status**: Built but not integrated with live trading yet

---

### **Testing & Analysis**

#### `historicData.py` - Historical Data Downloader
- **What it does**: Downloads historical price data from Yahoo Finance
- **Output**: Saves CSV file to `tests/historic_data.csv`
- **Configuration**:
  - `tickers = yq.Ticker('OPEN')` - Which stock to download
  - `period='60d'` - Last 60 days
  - `interval='5m'` - 5-minute bars
- **How to use**:
  1. Change ticker symbol if needed
  2. Run: `python3 historicData.py`
  3. CSV appears in `tests/historic_data.csv`

#### `tests/test1.py` - Strategy Backtester
- **What it does**: Tests trading strategies on historical data
- **Features**:
  - Simulates buy/sell decisions
  - Tracks returns and max drawdown
  - Tests different MACD thresholds
- **Current strategy**:
  - **BUY**: When histogram is very small (`abs(hist) < 0.01`)
  - **SELL**: When MACD starts declining but is still above signal
- **How to run**:
  1. Make sure `historic_data.csv` exists (run `historicData.py` first)
  2. `cd tests`
  3. `python3 test1.py`
- **Output**: Prints buy/sell signals, total return, max drawdown

---

## 🚀 How to Get Started

### 1. **First Time Setup**

```bash
# Clone/navigate to project
cd FX_Carry_Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. **Run Live Trading Monitor**

```bash
# Start the live stream
python3 livePull.py

# What you'll see:
# - Green/Red colored completed bars
# - BUY signals in green when MACD conditions met
# - SELL signals in red when MACD conditions met
# - All data logged to logs/ folder
```

**To change the stock**: Edit line 116 in `livePull.py`:
```python
ticker_symbol = "AAPL"  # Change to any ticker
```

### 3. **Backtest a Strategy**

```bash
# Step 1: Download historical data
python3 historicData.py

# Step 2: Run backtest
cd tests
python3 test1.py

# You'll see:
# - All buy/sell signals printed
# - Total return at the end
# - Max drawdown (biggest loss)
```

---

## 🔧 How to Add Improvements

### **Improvement 1: Change the Trading Strategy**

**File**: `livePull.py` (lines 23-31) or `tests/test1.py` (lines 31-40)

**Current logic**:
```python
def shouldBuy(macd, signal, hist):
    return macd > signal and hist > 0 and abs(macd - signal) < 0.008

def shouldSell(macd, signal, hist):
    return macd < signal and hist < 0 and macd_logs[-1]["macd"] < macd_logs[-2]["macd"]
```

**Ideas to try**:
- Add RSI indicator
- Use multiple timeframes
- Add stop-loss logic
- Require consecutive signals
- Add volume confirmation

**Example - More conservative buy**:
```python
def shouldBuy(macd, signal, hist):
    # Only buy when histogram is positive AND growing
    if len(macd_logs) < 2:
        return False
    return (hist > 0 and 
            macd > signal and 
            hist > macd_logs[-1]["hist"])  # Histogram increasing
```

### **Improvement 2: Integrate TradingBot for Portfolio Tracking**

**File**: `livePull.py`

**Add at top**:
```python
from TradingBot import TradingBot

# Create bot with $10,000 starting balance
bot = TradingBot("MyBot", 10000)
```

**In the signal detection section** (around line 100):
```python
if shouldBuy(macd, signal, hist):
    print(f"{GREEN}Signal to BUY detected!{RESET}")
    # Calculate how many shares to buy with 10% of balance
    shares = (bot.get_balance() * 0.1) / price
    bot.buy(symbol, shares, price)
    print(f"Bought {shares:.2f} shares. Balance: ${bot.get_balance():.2f}")
    
elif shouldSell(macd, signal, hist):
    print(f"{RED}Signal to SELL detected!{RESET}")
    # Sell all shares of this asset
    if symbol in bot.get_portfolio():
        shares = bot.get_portfolio()[symbol]
        bot.sell(symbol, shares, price)
        print(f"Sold {shares:.2f} shares. Balance: ${bot.get_balance():.2f}")
```

### **Improvement 3: Add New Technical Indicators**

**Create new file**: `RSI.py`
```python
import pandas as pd

def compute_rsi(bars, period=14):
    df = pd.DataFrame(bars)
    close = df["close"]
    
    # Calculate price changes
    delta = close.diff()
    
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).ewm(span=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period).mean()
    
    # Calculate RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]
```

**Use in livePull.py**:
```python
from RSI import compute_rsi

# In on_message function:
if len(barAggregator.bars) > 26:
    macd, signal, hist = compute_macd(barAggregator.bars)
    rsi = compute_rsi(barAggregator.bars)
    
    # Combined strategy
    if shouldBuy(macd, signal, hist) and rsi < 30:  # Oversold
        print(f"{GREEN}STRONG BUY - RSI oversold!{RESET}")
```

### **Improvement 4: Add Multiple Timeframes**

**File**: `livePull.py`

**Replace single aggregator with multiple**:
```python
# Multiple timeframes
agg_1min = BarAggregator(interval_seconds=60)
agg_5min = BarAggregator(interval_seconds=300)
agg_15min = BarAggregator(interval_seconds=900)

def on_message(msg):
    price = msg["price"]
    ts = msg["time"]
    
    # Update all timeframes
    agg_1min.update(price, ts)
    agg_5min.update(price, ts)
    agg_15min.update(price, ts)
    
    # Calculate MACD for each
    if len(agg_1min.bars) > 26:
        macd_1m, signal_1m, hist_1m = compute_macd(agg_1min.bars)
    if len(agg_5min.bars) > 26:
        macd_5m, signal_5m, hist_5m = compute_macd(agg_5min.bars)
    if len(agg_15min.bars) > 26:
        macd_15m, signal_15m, hist_15m = compute_macd(agg_15min.bars)
        
    # Trend alignment: buy when all timeframes bullish
    if (hist_1m > 0 and hist_5m > 0 and hist_15m > 0):
        print(f"{GREEN}STRONG BUY - All timeframes aligned!{RESET}")
```

### **Improvement 5: Better Logging & Analysis**

**Create**: `logger.py`
```python
import csv
from datetime import datetime

class TradeLogger:
    def __init__(self, filename="trades.csv"):
        self.filename = filename
        # Create file with headers if it doesn't exist
        try:
            with open(filename, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'symbol', 'price', 
                               'macd', 'signal', 'hist', 'balance'])
        except FileExistsError:
            pass
    
    def log_trade(self, action, symbol, price, macd, signal, hist, balance):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                action, symbol, price,
                f"{macd:.5f}", f"{signal:.5f}", f"{hist:.5f}",
                f"{balance:.2f}"
            ])
```

**Use in livePull.py**:
```python
from logger import TradeLogger

logger = TradeLogger("logs/trades.csv")

# When signal detected:
if shouldBuy(macd, signal, hist):
    logger.log_trade("BUY", symbol, price, macd, signal, hist, bot.get_balance())
```

### **Improvement 6: Add Real-time Alerts**

**Install**: `pip install plyer` (for desktop notifications)

**Add to livePull.py**:
```python
from plyer import notification

def send_alert(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

# When signal detected:
if shouldBuy(macd, signal, hist):
    send_alert("BUY SIGNAL", f"{symbol} at ${price:.2f}")
```

---

## 📊 Understanding the Data Flow

```
Yahoo Finance WebSocket
         ↓
    on_message() receives tick data
         ↓
    BarAggregator.update(price, timestamp)
         ↓
    Builds 5-minute OHLC bars
         ↓
    compute_macd(bars) calculates indicators
         ↓
    shouldBuy() / shouldSell() evaluate signals
         ↓
    Print alerts & log to files
```

---

## 🐛 Common Issues & Solutions

### **Issue**: Import errors when running test1.py
**Solution**: Make sure you're in the `tests/` directory and run `python3 test1.py`

### **Issue**: No data streaming in livePull.py
**Solution**: 
- Check if market is open
- Try a more liquid ticker (AAPL, TSLA, SPY)
- Check internet connection

### **Issue**: MACD not calculating
**Solution**: Need at least 26 bars. Wait a few minutes (26 × 5min = 130 minutes for 5-min bars)

### **Issue**: "os" module error in requirements.txt
**Solution**: Remove `os` from requirements.txt (it's built-in to Python)

---

## 🎓 Key Concepts to Understand

### **OHLC Bars (Candlesticks)**
- **Open**: First price in the time period
- **High**: Highest price in the time period  
- **Low**: Lowest price in the time period
- **Close**: Last price in the time period

### **MACD Indicator**
- **MACD Line**: Fast EMA - Slow EMA (shows momentum)
- **Signal Line**: Smoothed MACD (shows trend)
- **Histogram**: MACD - Signal (shows strength)

**Trading Signals**:
- MACD crosses **above** Signal = Bullish (potential buy)
- MACD crosses **below** Signal = Bearish (potential sell)

### **Backtesting**
Testing a strategy on historical data to see if it would have been profitable. Does NOT guarantee future performance.

---

## 📝 Next Steps / TODO

- [ ] Integrate TradingBot class with live trading
- [ ] Add risk management (stop-loss, take-profit)
- [ ] Implement multiple technical indicators (RSI, Bollinger Bands)
- [ ] Create a web dashboard for monitoring
- [ ] Add paper trading mode before live trading
- [ ] Calculate win rate, Sharpe ratio, other metrics
- [ ] Add configuration file for easy parameter changes
- [ ] Implement multi-symbol monitoring

---

## 📚 Useful Resources

- **Yahoo Finance API**: [yfinance documentation](https://github.com/ranaroussi/yfinance)
- **MACD Strategy**: [Investopedia MACD](https://www.investopedia.com/terms/m/macd.asp)
- **Pandas for Analysis**: [pandas documentation](https://pandas.pydata.org/)

---

## ⚠️ Important Warnings

1. **This is NOT financial advice** - Educational purposes only
2. **Do not use real money without thorough testing**
3. **Past performance ≠ future results**
4. **Always use paper trading first**
5. **Understand the risks** before trading real capital

---

**Questions?** Read the code comments, check the other README files, or experiment with backtesting first!
