# utils/validators.py
import yfinance as yf
import pandas as pd

def validate_tickers(tickers):
    """Validate list of tickers"""
    valid = []
    invalid = []
    
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", progress=False)
            if not df.empty:
                valid.append(t)
            else:
                invalid.append(t)
        except:
            invalid.append(t)
    
    return valid, invalid

def validate_single_ticker(ticker):
    """Validate single ticker"""
    try:
        df = yf.download(ticker, period="1mo", progress=False)
        return not df.empty
    except:
        return False