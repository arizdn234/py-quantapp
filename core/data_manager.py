# core/data_manager.py
import yfinance as yf
import pandas as pd
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

class DataManager:
    def __init__(self, cache_dir="data_cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, ticker):
        return os.path.join(self.cache_dir, f"{ticker}.parquet")
    
    def download(self, ticker, period="2y"):
        """Download fresh data from Yahoo Finance"""
        try:
            df = yf.download(ticker, period=period, progress=False)
            if df.empty:
                return None
            
            # Clean columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Save to cache
            cache_path = self._get_cache_path(ticker)
            df.to_parquet(cache_path)
            
            logging.info(f"Downloaded {ticker}")
            return df
        except Exception as e:
            logging.error(f"Error downloading {ticker}: {e}")
            return None
    
    def load(self, ticker):
        """Load cached data"""
        cache_path = self._get_cache_path(ticker)
        
        if os.path.exists(cache_path):
            try:
                return pd.read_parquet(cache_path)
            except Exception as e:
                logging.error(f"Error loading {ticker}: {e}")
                return None
        return None
    
    def update(self, ticker):
        """Update existing data with latest prices"""
        df = self.load(ticker)
        
        if df is None:
            return self.download(ticker)
        
        # Check if update needed
        last_date = df.index[-1]
        today = datetime.now().date()
        
        if last_date.date() < today - timedelta(days=1):
            try:
                # Download only missing data
                new_df = yf.download(ticker, start=last_date + timedelta(days=1), 
                                    end=today, progress=False)
                
                if not new_df.empty:
                    if isinstance(new_df.columns, pd.MultiIndex):
                        new_df.columns = new_df.columns.get_level_values(0)
                    
                    df = pd.concat([df, new_df])
                    df = df[~df.index.duplicated(keep='last')]
                    
                    # Save updated data
                    cache_path = self._get_cache_path(ticker)
                    df.to_parquet(cache_path)
                    
                    logging.info(f"Updated {ticker}")
            
            except Exception as e:
                logging.error(f"Error updating {ticker}: {e}")
        
        return df