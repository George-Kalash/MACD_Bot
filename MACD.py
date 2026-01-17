import pandas as pd

def compute_macd(bars):
    df = pd.DataFrame(bars)
    close = df["close"]

    ema_fast = close.ewm(span=18).mean() # Changed from 12 to 18. Showed a fine result when tested
    ema_slow = close.ewm(span=26).mean()

    macd = ema_fast - ema_slow
    signal = macd.ewm(span=9).mean()
    hist = macd - signal

    return macd.iloc[-1], signal.iloc[-1], hist.iloc[-1]

