import asyncio
import yfinance as yf

latest = {}
last_seen = {}
def on_message(msg):
    symbol = msg["id"]
    price = msg["price"]
    ts = msg["time"]

    prev = last_seen.get(symbol)

    if prev is None or prev["price"] != price or prev["time"] != ts:
        last_seen[symbol] = msg
        print(last_seen[symbol])

async def live_data_stream(ticker_symbol, callback):
  async with yf.AsyncWebSocket() as ws:
    await ws.subscribe([ticker_symbol])
    await ws.listen(callback)
    

async def main():
  ticker_symbol = "AAPL"
    
  stream_task = asyncio.create_task(live_data_stream(ticker_symbol, on_message))

  try:
    while True:
      if ticker_symbol in latest:
        
        print(f"Latest data for {ticker_symbol}: {latest[ticker_symbol]}")
      await asyncio.sleep(1)
  finally:
    stream_task.cancel()
  
      

asyncio.run(main())