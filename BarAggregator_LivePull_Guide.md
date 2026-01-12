# Using BarAggregator with LivePull

This guide explains how to integrate the `BarAggregator` class with the live data streaming functionality in `livePull.py` to aggregate real-time price data into OHLC (Open, High, Low, Close) bars.

## Overview

- **BarAggregator**: Aggregates individual price ticks into time-based OHLC bars
- **livePull.py**: Streams live market data from Yahoo Finance using websockets

## How BarAggregator Works

The `BarAggregator` class takes streaming price data and converts it into candlestick bars over a specified time interval.

### Key Features

- **Time-based buckets**: Groups prices into fixed time intervals (default: 60 seconds)
- **OHLC tracking**: Maintains Open, High, Low, and Close for each bar
- **Auto-rotation**: Automatically creates a new bar when the time interval changes
- **History storage**: Keeps the last 500 bars in memory

### Parameters

- `interval_seconds`: The time window for each bar (default: 60 seconds)

### Methods

- `update(price: float, ts_ms: int)`: Updates the aggregator with a new price tick
  - `price`: The current price
  - `ts_ms`: Timestamp in milliseconds

### Data Structure

Each bar is a dictionary with:
```python
{
  "bucket": int,      # Unix timestamp of the bar's start time
  "open": float,      # First price in the interval
  "high": float,      # Highest price in the interval
  "low": float,       # Lowest price in the interval
  "close": float      # Most recent price in the interval
}
```

## Integration Example

Here's how to integrate `BarAggregator` with `livePull.py`:

### Step 1: Import and Initialize

```python
import asyncio
import yfinance as yf
from barAggregator import BarAggregator

# Create a BarAggregator instance
# For 1-minute bars:
aggregator = BarAggregator(interval_seconds=60)

# For 5-minute bars:
# aggregator = BarAggregator(interval_seconds=300)
```

### Step 2: Update the Callback Function

Modify the `on_message` callback to feed data into the aggregator:

```python
def on_message(msg):
    symbol = msg["id"]
    price = msg["price"]
    ts_ms = msg["time"]  # Timestamp in milliseconds
    
    # Update the bar aggregator
    aggregator.update(price, ts_ms)
    
    # Access the current bar being built
    if aggregator.current_bar:
        print(f"Current bar: {aggregator.current_bar}")
    
    # Access completed bars
    if len(aggregator.bars) > 0:
        latest_completed_bar = aggregator.bars[-1]
        print(f"Latest completed bar: {latest_completed_bar}")
```

### Step 3: Complete Example

```python
import asyncio
import yfinance as yf
from barAggregator import BarAggregator
from datetime import datetime, timezone

# Initialize the aggregator for 1-minute bars
aggregator = BarAggregator(interval_seconds=60)

def on_message(msg):
    symbol = msg["id"]
    price = msg["price"]
    ts_ms = msg["time"]
    
    # Update aggregator
    aggregator.update(price, ts_ms)
    
    # Print current bar status
    if aggregator.current_bar:
        bucket_time = datetime.fromtimestamp(
            aggregator.current_bar["bucket"], 
            tz=timezone.utc
        )
        print(f"[{bucket_time}] O:{aggregator.current_bar['open']:.2f} "
              f"H:{aggregator.current_bar['high']:.2f} "
              f"L:{aggregator.current_bar['low']:.2f} "
              f"C:{aggregator.current_bar['close']:.2f}")

async def live_data_stream(ticker_symbol, callback):
    async with yf.AsyncWebSocket() as ws:
        await ws.subscribe([ticker_symbol])
        await ws.listen(callback)

async def main():
    ticker_symbol = "EURUSD=X"  # Example FX pair
    
    stream_task = asyncio.create_task(
        live_data_stream(ticker_symbol, on_message)
    )
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        stream_task.cancel()

asyncio.run(main())
```

## Common Use Cases

### 1. Real-time Chart Data
```python
# Access all historical bars for charting
all_bars = list(aggregator.bars)
```

### 2. Technical Analysis
```python
# Get the last N completed bars for indicator calculation
if len(aggregator.bars) >= 20:
    recent_bars = list(aggregator.bars)[-20:]
    # Calculate moving average, MACD, etc.
```

### 3. Trading Signals
```python
def on_message(msg):
    aggregator.update(msg["price"], msg["time"])
    
    # When a new bar completes, check for trading signals
    if len(aggregator.bars) > prev_bar_count:
        last_bar = aggregator.bars[-1]
        # Analyze the completed bar for trading opportunities
```

### 4. Different Time Frames
```python
# Create multiple aggregators for different timeframes
agg_1min = BarAggregator(interval_seconds=60)
agg_5min = BarAggregator(interval_seconds=300)
agg_15min = BarAggregator(interval_seconds=900)

def on_message(msg):
    price = msg["price"]
    ts_ms = msg["time"]
    
    # Update all timeframes simultaneously
    agg_1min.update(price, ts_ms)
    agg_5min.update(price, ts_ms)
    agg_15min.update(price, ts_ms)
```

## Important Notes

1. **Timestamp Format**: The `update()` method expects timestamps in milliseconds (as provided by yfinance websocket)

2. **Current Bar**: `aggregator.current_bar` represents the bar currently being built and will update with each new price tick

3. **Completed Bars**: `aggregator.bars` contains only completed bars (previous intervals)

4. **Memory Management**: The aggregator stores a maximum of 500 bars by default. Older bars are automatically removed.

5. **Time Alignment**: Bars align to Unix timestamp boundaries. A 60-second bar starting at 10:30:00 will complete at 10:30:59.

## Troubleshooting

**Issue**: Bars not updating
- Check that timestamps are in milliseconds
- Verify the ticker symbol is actively trading

**Issue**: Unexpected bar intervals
- Ensure `interval_seconds` is set correctly
- Check system time is synchronized

**Issue**: Missing data
- Market may be closed or symbol not available
- Check websocket connection status
