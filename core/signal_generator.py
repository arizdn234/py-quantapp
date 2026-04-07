# core/signal_generator.py
import pandas as pd

class SignalGenerator:
    def __init__(self):
        self.rsi_oversold = 30
        self.rsi_overbought = 70
    
    def generate_signal(self, feat_row):
        """Generate trading signal based on features"""
        if pd.isna(feat_row["ma20"]) or pd.isna(feat_row["ma50"]):
            return "HOLD", 0
        
        signal = "HOLD"
        confidence = 0
        reasons = []
        
        # Check for BUY signals
        buy_score = 0
        if feat_row["ma20"] > feat_row["ma50"]:
            buy_score += 2
            reasons.append("Golden Cross")
        
        if feat_row["rsi"] < self.rsi_oversold:
            buy_score += 2
            reasons.append("Oversold")
        
        if feat_row["price_to_ma20"] > 0:
            buy_score += 1
            reasons.append("Above MA20")
        
        if feat_row["macd"] > feat_row["macd_signal"]:
            buy_score += 1
            reasons.append("MACD Bullish")
        
        if feat_row["bb_position"] < 0.2:
            buy_score += 1
            reasons.append("Near Lower BB")
        
        # Check for SELL signals
        sell_score = 0
        if feat_row["ma20"] < feat_row["ma50"]:
            sell_score += 2
            reasons.append("Death Cross")
        
        if feat_row["rsi"] > self.rsi_overbought:
            sell_score += 2
            reasons.append("Overbought")
        
        if feat_row["price_to_ma20"] < 0:
            sell_score += 1
            reasons.append("Below MA20")
        
        if feat_row["macd"] < feat_row["macd_signal"]:
            sell_score += 1
            reasons.append("MACD Bearish")
        
        if feat_row["bb_position"] > 0.8:
            sell_score += 1
            reasons.append("Near Upper BB")
        
        # Determine final signal
        if buy_score >= 3:
            signal = "BUY"
            confidence = min(buy_score / 6, 1.0)
        elif sell_score >= 3:
            signal = "SELL"
            confidence = min(sell_score / 6, 1.0)
        
        return signal, confidence, reasons
    
    def get_signal_strength(self, signal):
        """Get signal strength for display"""
        strengths = {
            "BUY": "STRONG BUY",
            "SELL": "STRONG SELL"
        }
        return strengths.get(signal, "HOLD")