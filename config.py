# config.py
import pandas as pd
from datetime import datetime

class Config:
    # Data settings
    DEFAULT_PERIOD = "2y"
    CACHE_TTL = 3600  # 1 hour
    
    # Feature settings
    RSI_PERIOD = 14
    MA_SHORT = 20
    MA_LONG = 50
    
    # Signal thresholds
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # Display settings
    CHART_STYLE = "yahoo"
    CHART_VOLUME = True
    
    # Date settings
    TODAY = datetime.today().strftime("%Y-%m-%d")