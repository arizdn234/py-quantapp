# core/ticker_manager.py
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

class TickerManager:
    def __init__(self, filename="tickers.json"):
        self.filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump(["AAPL", "GOOGL", "MSFT"], f)
    
    def load(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading tickers: {e}")
            return []
    
    def save(self, tickers):
        try:
            with open(self.filename, "w") as f:
                json.dump(tickers, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving tickers: {e}")
            return False
    
    def add(self, ticker):
        tickers = self.load()
        if ticker not in tickers:
            tickers.append(ticker)
            return self.save(tickers)
        return False
    
    def remove(self, ticker):
        tickers = self.load()
        if ticker in tickers:
            tickers.remove(ticker)
            return self.save(tickers)
        return False
    
    def update_all(self, tickers):
        return self.save(tickers)