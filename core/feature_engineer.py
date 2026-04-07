# core/feature_engineer.py
import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self):
        self.rsi_period = 14
        self.ma_short = 20
        self.ma_long = 50
    
    def calculate_rsi(self, prices):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        exp_fast = prices.ewm(span=fast, adjust=False).mean()
        exp_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = exp_fast - exp_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, rolling_mean, lower_band
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def transform(self, df):
        """Generate all features"""
        feat = pd.DataFrame(index=df.index)
        
        # Price features
        feat["Close"] = df["Close"]
        feat["Open"] = df["Open"]
        feat["High"] = df["High"]
        feat["Low"] = df["Low"]
        feat["Volume"] = df["Volume"]
        
        # Returns
        feat["ret1"] = df["Close"].pct_change()
        feat["ret5"] = df["Close"].pct_change(5)
        feat["ret20"] = df["Close"].pct_change(20)
        
        # Moving Averages
        feat["ma20"] = df["Close"].rolling(window=self.ma_short).mean()
        feat["ma50"] = df["Close"].rolling(window=self.ma_long).mean()
        feat["ma200"] = df["Close"].rolling(window=200).mean()
        
        # Price relative to MA
        feat["price_to_ma20"] = df["Close"] / feat["ma20"] - 1
        feat["price_to_ma50"] = df["Close"] / feat["ma50"] - 1
        
        # RSI
        feat["rsi"] = self.calculate_rsi(df["Close"])
        
        # MACD
        macd, macd_signal, macd_hist = self.calculate_macd(df["Close"])
        feat["macd"] = macd
        feat["macd_signal"] = macd_signal
        feat["macd_histogram"] = macd_hist
        
        # Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(df["Close"])
        feat["bb_upper"] = upper
        feat["bb_middle"] = middle
        feat["bb_lower"] = lower
        feat["bb_width"] = (upper - lower) / middle
        feat["bb_position"] = (df["Close"] - lower) / (upper - lower)
        
        # ATR
        feat["atr"] = self.calculate_atr(df)
        feat["atr_pct"] = feat["atr"] / df["Close"]
        
        # Volume features
        feat["volume_ma"] = df["Volume"].rolling(window=20).mean()
        feat["volume_ratio"] = df["Volume"] / feat["volume_ma"]
        
        # Volatility
        feat["volatility"] = feat["ret1"].rolling(window=20).std()
        
        return feat.dropna()