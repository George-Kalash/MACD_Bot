import asyncio
import yfinance as yf
from barAggregator import BarAggregator
from MACD import compute_macd
from datetime import datetime, timezone
import os

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'
color = RESET
SHOULD_PRINT_BARS = False
INT_SECONDS = 10

barAggregator = BarAggregator(interval_seconds=INT_SECONDS)

latest = {}
last_seen = {}
latest_completed_bar = None
macd_logs = []
macd_log = {}

test_results = []

can_SELL = False
can_BUY = True
THRESHOLD = 0.01

buy_price = 0
total_return = 0

max_drawdown = 0

def shouldBuy(macd, signal, hist):
  # Simple MACD strategy: Buy when MACD crosses above Signal line
  return abs(hist) < THRESHOLD 

def shouldSell(macd, signal, hist):
  # Simple MACD strategy: Sell when MACD crosses below Signal line
  if len(macd_logs) < 2:
    return False
  return macd < macd_logs[-2]["macd"] and macd > signal and hist > 0


def on_message(msg):
  global can_BUY, can_SELL, buy_price, total_return, max_drawdown
  symbol = msg["id"]
  price = msg["price"]
  ts = msg["time"]
  
  barAggregator.update(price, int(ts))


  if barAggregator.current_bar:
    bucket_time = datetime.fromtimestamp(
      barAggregator.current_bar["bucket"], 
      tz=timezone.utc
    )
    # color coding
    if barAggregator.current_bar["close"] >= barAggregator.current_bar["open"]:
      color = GREEN
    else:
      color = RED
    
    if SHOULD_PRINT_BARS: 
      print(f"[{bucket_time}] O:{barAggregator.current_bar['open']:.2f} "
          f"H:{barAggregator.current_bar['high']:.2f} "
          f"L:{barAggregator.current_bar['low']:.2f} "
          f"C:{color}{barAggregator.current_bar['close']:.2f}{RESET}")
  
  if len(barAggregator.bars) > 0:
    
    global latest_completed_bar
    if latest_completed_bar == None or latest_completed_bar != barAggregator.bars[-1]:
      latest_completed_bar = barAggregator.bars[-1] 
      # color coding
      if latest_completed_bar["close"] >= latest_completed_bar["open"]: 
        color = GREEN
      else:
        color = RED
      print(f"Latest completed bar: {color}{latest_completed_bar}{RESET}")
      try: 
        os.makedirs("logs", exist_ok=True)
        with open(f"logs/log_{symbol}", "a") as f:
          f.write(f"{latest_completed_bar}\n")
      except Exception as e:
        print(f"Error writing to log file: {e}")

  prev = last_seen.get(symbol)

  if len(barAggregator.bars) > 26:
    # calculate MACD
    macd, signal, hist = compute_macd(barAggregator.bars)
    macd_log = {
        "timestamp": bucket_time,
        "macd": macd,
        "signal": signal,
        "hist": hist
    }
    macd_logs.append(macd_log)
    # write macd to file
    try: 
      with open(f"logs/macd_{symbol}", "a") as f:
        f.write(f"{macd_log}\n")
    except Exception as e:
      print(f"Error writing MACD to log file: {e}")
    if SHOULD_PRINT_BARS:
      print(f"MACD: {macd:.5f}, Signal: {signal:.5f}, Hist: {hist:.5f}")
    if can_BUY and shouldBuy(macd, signal, hist):
      test_results.append(f"BUY signal at {barAggregator.bars[-1]['bucket']} with price {price}")
      can_BUY = False
      can_SELL = True
      buy_price = price
      print(f"BUY signal at {barAggregator.bars[-1]['bucket']} with price {price}")
    elif can_SELL and shouldSell(macd, signal, hist):
      test_results.append(f"SELL signal at {barAggregator.bars[-1]['bucket']} with price {price}")
      can_SELL = False
      can_BUY = True
      total_return += (price - buy_price)
      max_drawdown = min(max_drawdown, price - buy_price)
      print(f"SELL signal at {barAggregator.bars[-1]['bucket']} with price {price}, retutn: {(price - buy_price)}")
  if prev is None or prev["price"] != price or prev["time"] != ts:
    last_seen[symbol] = msg
    # print(last_seen[symbol])

async def live_data_stream(ticker_symbol, callback):
  async with yf.AsyncWebSocket() as ws:
    await ws.subscribe([ticker_symbol])
    await ws.listen(callback)
    

async def main():
  ticker_symbol = "EVTV"
    
  stream_task = asyncio.create_task(live_data_stream(ticker_symbol, on_message))

  try:
    while True:
        
        # print(f"Latest data for {ticker_symbol}: {latest[ticker_symbol]}")
      await asyncio.sleep(1)
  except KeyboardInterrupt:
    print("\nStopping stream...")
  finally:
    stream_task.cancel()
  
      

asyncio.run(main())