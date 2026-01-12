from collections import deque
from datetime import datetime, timezone

class BarAggregator:
    def __init__(self, interval_seconds=60):
        self.interval = interval_seconds
        self.current_bar = None
        self.bars = deque(maxlen=500)

    def update(self, price: float, ts_ms: int):
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        bucket = int(ts.timestamp() // self.interval) * self.interval

        if self.current_bar is None or self.current_bar["bucket"] != bucket:
            if self.current_bar:
                self.bars.append(self.current_bar)

            self.current_bar = {
                "bucket": bucket,
                "open": price,
                "high": price,
                "low": price,
                "close": price
            }
        else:
            self.current_bar["high"] = max(self.current_bar["high"], price)
            self.current_bar["low"] = min(self.current_bar["low"], price)
            self.current_bar["close"] = price
