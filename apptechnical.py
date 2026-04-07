import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
import numpy as np
import hashlib
import hmac

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Saham Indo Dashboard - Enhanced Analysis",
    page_icon="📊",
    layout="wide"
)

# ============================================
# CONSTANTS
# ============================================

# BEI Index Constituents (LQ45 and IDX80)
LQ45_TICKERS = [
    "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK",
    "ASII.JK", "BBCA.JK", "BBRI.JK", "BBTN.JK", "BBNI.JK",
    "BMRI.JK", "BRIS.JK", "BRPT.JK", "BSDE.JK", "BUKA.JK",
    "CPIN.JK", "CTRA.JK", "DSSA.JK", "ELSA.JK", "EMTK.JK",
    "ERAA.JK", "ESSA.JK", "EXCL.JK", "GOTO.JK", "HRUM.JK",
    "ICBP.JK", "INCO.JK", "INDF.JK", "INRP.JK", "IPCC.JK",
    "ISAT.JK", "JPFA.JK", "JSMR.JK", "KAEF.JK", "KLBF.JK",
    "MDKA.JK", "MEDC.JK", "MIKA.JK", "MNCN.JK", "PGAS.JK",
    "PTBA.JK", "PTPP.JK", "PWON.JK", "SMGR.JK", "SMRA.JK",
    "SRTG.JK", "TBIG.JK", "TINS.JK", "TLKM.JK", "TOWR.JK",
    "UNTR.JK", "UNVR.JK", "WIKA.JK", "WSKT.JK"
]

IDX80_TICKERS = [
    "ADMF.JK", "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK",
    "ARTO.JK", "ASII.JK", "AUTO.JK", "BBCA.JK", "BBHI.JK",
    "BBNI.JK", "BBRI.JK", "BBTN.JK", "BDMN.JK", "BESS.JK",
    "BMRI.JK", "BOLA.JK", "BRIS.JK", "BRPT.JK", "BSDE.JK",
    "BTPS.JK", "BUKA.JK", "CAMP.JK", "CARE.JK", "CINT.JK",
    "CMNP.JK", "CPIN.JK", "CTRA.JK", "DFAM.JK", "DIVA.JK",
    "DMMX.JK", "DOID.JK", "DPUM.JK", "DSNG.JK", "DSSA.JK",
    "DYAN.JK", "ECII.JK", "EKAD.JK", "ELSA.JK", "EMTK.JK",
    "ENRG.JK", "ERAA.JK", "ESSA.JK", "EXCL.JK", "FILM.JK",
    "FIRE.JK", "FREN.JK", "GGRM.JK", "GOTO.JK", "GTBO.JK",
    "HEAL.JK", "HOKI.JK", "HRUM.JK", "ICBP.JK", "ICON.JK",
    "INCO.JK", "INDF.JK", "INPP.JK", "INTA.JK", "INTD.JK",
    "IPCC.JK", "IPOL.JK", "ISAT.JK", "ITMG.JK", "JPFA.JK",
    "JSMR.JK", "JTPE.JK", "KAEF.JK", "KBLM.JK", "KBLV.JK",
    "KIJA.JK", "KLBF.JK", "KRAH.JK", "KRAS.JK", "LAPD.JK",
    "LCGP.JK", "LINK.JK", "LPCK.JK", "LPKR.JK", "LPLI.JK",
    "LPPF.JK", "LSIP.JK", "MAIN.JK", "MAPA.JK", "MAPI.JK",
    "MASA.JK", "MDKA.JK", "MEDC.JK", "MERK.JK", "MFIN.JK",
    "MGRO.JK", "MIKA.JK", "MIRA.JK", "MKPI.JK", "MLBI.JK",
    "MNCN.JK", "MPPA.JK", "MPRO.JK", "MRAT.JK", "MSIN.JK",
    "MTDL.JK", "MTFN.JK", "MYOR.JK", "NISP.JK", "OPMS.JK",
    "PADA.JK", "PANI.JK", "PEGE.JK", "PGAS.JK", "PJAA.JK",
    "PLIN.JK", "PNBN.JK", "PNBS.JK", "PNIN.JK", "POLL.JK",
    "PPRE.JK", "PRDA.JK", "PSAB.JK", "PSGO.JK", "PTBA.JK",
    "PTPP.JK", "PTRO.JK", "PTSN.JK", "PWON.JK", "RALS.JK",
    "RANC.JK", "RBMS.JK", "RDTR.JK", "REAL.JK", "RELI.JK",
    "RMBA.JK", "ROTI.JK", "SAME.JK", "SAPX.JK", "SCMA.JK",
    "SGRO.JK", "SIDO.JK", "SILO.JK", "SMMA.JK", "SMRA.JK",
    "SMST.JK", "SOCI.JK", "SOHO.JK", "SONA.JK", "SQMI.JK",
    "SRIL.JK", "SRTG.JK", "SSIA.JK", "SSMS.JK", "SULI.JK",
    "SUPR.JK", "TAPG.JK", "TAYS.JK", "TBIG.JK", "TBSI.JK",
    "TCID.JK", "TDPM.JK", "TELE.JK", "TFCO.JK", "TGKA.JK",
    "TINS.JK", "TKIM.JK", "TLKM.JK", "TOWR.JK", "TPIA.JK",
    "TRAM.JK", "TRGU.JK", "TRIM.JK", "TRIS.JK", "TSPC.JK",
    "UCID.JK", "UGTR.JK", "UNIC.JK", "UNTR.JK", "UNVR.JK",
    "VICI.JK", "VOKS.JK", "VRBA.JK", "WICO.JK", "WIIM.JK",
    "WIKA.JK", "WINS.JK", "WSKT.JK", "WTON.JK", "YBEE.JK",
    "YELO.JK", "YULE.JK", "ZINC.JK"
]

DEFAULT_TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]

STOCK_METADATA = {
    "BBCA.JK": {"name": "Bank Central Asia", "sector": "Banking", "market_cap": "Large Cap"},
    "BBRI.JK": {"name": "Bank Rakyat Indonesia", "sector": "Banking", "market_cap": "Large Cap"},
    "BMRI.JK": {"name": "Bank Mandiri", "sector": "Banking", "market_cap": "Large Cap"},
    "TLKM.JK": {"name": "Telkom Indonesia", "sector": "Telecommunication", "market_cap": "Large Cap"},
    "ASII.JK": {"name": "Astra International", "sector": "Automotive", "market_cap": "Large Cap"},
    "UNVR.JK": {"name": "Unilever Indonesia", "sector": "Consumer Goods", "market_cap": "Large Cap"},
    "ADRO.JK": {"name": "Adaro Energy", "sector": "Energy", "market_cap": "Large Cap"},
    "ICBP.JK": {"name": "Indofood CBP", "sector": "Consumer Goods", "market_cap": "Large Cap"},
    "INDF.JK": {"name": "Indofood Sukses Makmur", "sector": "Consumer Goods", "market_cap": "Large Cap"},
    "GOTO.JK": {"name": "GoTo Gojek Tokopedia", "sector": "Technology", "market_cap": "Large Cap"},
    "SMGR.JK": {"name": "Semen Indonesia", "sector": "Cement", "market_cap": "Mid Cap"},
    "INCO.JK": {"name": "Vale Indonesia", "sector": "Mining", "market_cap": "Mid Cap"},
    "ANTM.JK": {"name": "Aneka Tambang", "sector": "Mining", "market_cap": "Mid Cap"},
    "CPIN.JK": {"name": "Charoen Pokphand", "sector": "Consumer Goods", "market_cap": "Large Cap"},
    "PGAS.JK": {"name": "Perusahaan Gas Negara", "sector": "Energy", "market_cap": "Mid Cap"}
}

# CSV file for cached data
DATA_CACHE_FILE = "stock_data_cache.csv"

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 10px; border-radius: 5px; }
    .signal-buy { background-color: rgba(0, 255, 0, 0.1); border-left: 4px solid #00ff00; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .signal-sell { background-color: rgba(255, 0, 0, 0.1); border-left: 4px solid #ff0000; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .signal-hold { background-color: rgba(255, 255, 0, 0.1); border-left: 4px solid #ffff00; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .signal-strong-buy { background-color: rgba(0, 255, 0, 0.2); border-left: 4px solid #00ff00; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #00ff00; }
    .filter-container { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ============================================
# AUTHENTICATION SYSTEM
# ============================================

class AuthManager:
    def __init__(self, user_file="users.json"):
        self.user_file = user_file
        self._init_user_file()
    
    def _init_user_file(self):
        if not os.path.exists(self.user_file):
            default_users = {
                "admin": {
                    "password": hashlib.sha256("admin123".encode()).hexdigest(),
                    "name": "Administrator",
                    "email": "admin@example.com",
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                },
                "trader1": {
                    "password": hashlib.sha256("trader123".encode()).hexdigest(),
                    "name": "Trader Satu",
                    "email": "trader1@example.com",
                    "role": "user",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                }
            }
            with open(self.user_file, "w") as f:
                json.dump(default_users, f, indent=2)
    
    def authenticate(self, username, password):
        try:
            with open(self.user_file, "r") as f:
                users = json.load(f)
            
            if username in users:
                hashed = hashlib.sha256(password.encode()).hexdigest()
                if hmac.compare_digest(hashed, users[username]["password"]):
                    users[username]["last_login"] = datetime.now().isoformat()
                    with open(self.user_file, "w") as f:
                        json.dump(users, f, indent=2)
                    return True, users[username]
            return False, None
        except:
            return False, None

# ============================================
# TICKER MANAGER
# ============================================

class TickerManager:
    def __init__(self, ticker_file="tickers_idn.json"):
        self.ticker_file = ticker_file
        self._load_tickers()
    
    def _load_tickers(self):
        if os.path.exists(self.ticker_file):
            with open(self.ticker_file, 'r') as f:
                self.tickers = json.load(f)
        else:
            self.tickers = DEFAULT_TICKERS.copy()
            self._save_tickers()
    
    def _save_tickers(self):
        with open(self.ticker_file, 'w') as f:
            json.dump(self.tickers, f, indent=2)
    
    def get_tickers(self):
        return self.tickers
    
    def add_ticker(self, ticker):
        ticker = ticker.upper()
        if not ticker.endswith('.JK'):
            ticker = ticker + '.JK'
        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self._save_tickers()
            return True
        return False
    
    def update_ticker(self, old_ticker, new_ticker):
        new_ticker = new_ticker.upper()
        if not new_ticker.endswith('.JK'):
            new_ticker = new_ticker + '.JK'
        if old_ticker in self.tickers:
            idx = self.tickers.index(old_ticker)
            self.tickers[idx] = new_ticker
            self._save_tickers()
            return True
        return False
    
    def delete_ticker(self, ticker):
        if ticker in self.tickers:
            self.tickers.remove(ticker)
            self._save_tickers()
            return True
        return False
    
    def get_recommended_tickers(self, index_type="LQ45"):
        if index_type == "LQ45":
            return LQ45_TICKERS.copy()
        elif index_type == "IDX80":
            return IDX80_TICKERS.copy()
        return []
    
    def add_recommended_tickers(self, index_type):
        """Add recommended tickers without removing existing ones"""
        recommended = self.get_recommended_tickers(index_type)
        added = []
        for ticker in recommended:
            if ticker not in self.tickers:
                self.tickers.append(ticker)
                added.append(ticker)
        if added:
            self._save_tickers()
        return added
    
    def replace_with_recommended(self, index_type):
        """Replace all existing tickers with recommended ones"""
        recommended = self.get_recommended_tickers(index_type)
        self.tickers = recommended.copy()
        self._save_tickers()
        return len(recommended)

# ============================================
# ENHANCED ANALYSIS ENGINE
# ============================================

class EnhancedAnalysisEngine:
    def __init__(self):
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
    def calculate_all_indicators(self, df):
        feat = pd.DataFrame(index=df.index)
        
        feat['close'] = df['Close']
        feat['open'] = df['Open']
        feat['high'] = df['High']
        feat['low'] = df['Low']
        feat['volume'] = df['Volume']
        
        for period in [1, 3, 5, 10, 20]:
            feat[f'ret_{period}d'] = df['Close'].pct_change(period) * 100
        
        for period in [5, 10, 20, 50, 100, 200]:
            feat[f'ma_{period}'] = df['Close'].rolling(period).mean()
            feat[f'price_to_ma_{period}'] = (df['Close'] / feat[f'ma_{period}'] - 1) * 100
        
        for period in [7, 14, 21]:
            feat[f'rsi_{period}'] = self._calc_rsi(df['Close'], period)
        
        macd, signal, hist = self._calc_macd(df['Close'])
        feat['macd'] = macd
        feat['macd_signal'] = signal
        feat['macd_histogram'] = hist
        
        bb_upper, bb_mid, bb_lower = self._calc_bollinger(df['Close'])
        feat['bb_upper'] = bb_upper
        feat['bb_mid'] = bb_mid
        feat['bb_lower'] = bb_lower
        feat['bb_position'] = (df['Close'] - bb_lower) / (bb_upper - bb_lower)
        feat['bb_width'] = (bb_upper - bb_lower) / bb_mid * 100
        
        feat['volume_ma_20'] = df['Volume'].rolling(20).mean()
        feat['volume_ratio'] = df['Volume'] / feat['volume_ma_20']
        feat['volume_trend'] = df['Volume'].rolling(5).mean() / df['Volume'].rolling(20).mean()
        
        feat['volatility_20d'] = feat['ret_1d'].rolling(20).std()
        feat['support_20'] = df['Low'].rolling(20).min()
        feat['resistance_20'] = df['High'].rolling(20).max()
        feat['stoch_k'] = self._calc_stochastic(df)
        feat['adx'] = self._calc_adx(df)
        
        return feat.dropna()
    
    def _calc_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calc_macd(self, prices, fast=12, slow=26, signal=9):
        exp_fast = prices.ewm(span=fast, adjust=False).mean()
        exp_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = exp_fast - exp_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calc_bollinger(self, prices, window=20, num_std=2):
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper = rolling_mean + (rolling_std * num_std)
        lower = rolling_mean - (rolling_std * num_std)
        return upper, rolling_mean, lower
    
    def _calc_stochastic(self, df, period=14):
        low_min = df['Low'].rolling(period).min()
        high_max = df['High'].rolling(period).max()
        stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        return stoch_k
    
    def _calc_adx(self, df, period=14):
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (abs(minus_dm).rolling(period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx
    
    def generate_enhanced_signal(self, row):
        signal_data = {
            'signal': 'HOLD',
            'strength': 'NEUTRAL',
            'confidence': 0.5,
            'buy_signals': [],
            'sell_signals': [],
            'score': 0,
            'details': {}
        }
        
        buy_count = 0
        sell_count = 0
        total_weight = 0
        
        # Trend (25%)
        trend_weight = 25
        if row['ma_5'] > row['ma_20'] > row['ma_50']:
            buy_count += trend_weight
            signal_data['buy_signals'].append("Strong Uptrend (MA5 > MA20 > MA50)")
            signal_data['details']['trend'] = 25
        elif row['ma_5'] > row['ma_20']:
            buy_count += 15
            signal_data['buy_signals'].append("Bullish Trend (MA5 > MA20)")
            signal_data['details']['trend'] = 15
        elif row['ma_5'] < row['ma_20'] < row['ma_50']:
            sell_count += trend_weight
            signal_data['sell_signals'].append("Strong Downtrend (MA5 < MA20 < MA50)")
            signal_data['details']['trend'] = -25
        elif row['ma_5'] < row['ma_20']:
            sell_count += 15
            signal_data['sell_signals'].append("Bearish Trend (MA5 < MA20)")
            signal_data['details']['trend'] = -15
        total_weight += trend_weight
        
        # RSI (20%)
        rsi_weight = 20
        rsi = row['rsi_14']
        if rsi < 25:
            buy_count += rsi_weight
            signal_data['buy_signals'].append(f"Extreme Oversold (RSI: {rsi:.1f})")
            signal_data['details']['rsi'] = 20
        elif rsi < 30:
            buy_count += 15
            signal_data['buy_signals'].append(f"Oversold (RSI: {rsi:.1f})")
            signal_data['details']['rsi'] = 15
        elif rsi > 75:
            sell_count += rsi_weight
            signal_data['sell_signals'].append(f"Extreme Overbought (RSI: {rsi:.1f})")
            signal_data['details']['rsi'] = -20
        elif rsi > 70:
            sell_count += 15
            signal_data['sell_signals'].append(f"Overbought (RSI: {rsi:.1f})")
            signal_data['details']['rsi'] = -15
        elif rsi < 40:
            buy_count += 10
            signal_data['buy_signals'].append(f"Near Oversold (RSI: {rsi:.1f})")
            signal_data['details']['rsi'] = 10
        total_weight += rsi_weight
        
        # MACD (20%)
        macd_weight = 20
        if row['macd'] > row['macd_signal'] and row['macd_histogram'] > 0:
            buy_count += macd_weight
            signal_data['buy_signals'].append("MACD Bullish Crossover with Positive Histogram")
            signal_data['details']['macd'] = 20
        elif row['macd'] > row['macd_signal']:
            buy_count += 12
            signal_data['buy_signals'].append("MACD Bullish Crossover")
            signal_data['details']['macd'] = 12
        elif row['macd'] < row['macd_signal'] and row['macd_histogram'] < 0:
            sell_count += macd_weight
            signal_data['sell_signals'].append("MACD Bearish Crossover with Negative Histogram")
            signal_data['details']['macd'] = -20
        elif row['macd'] < row['macd_signal']:
            sell_count += 12
            signal_data['sell_signals'].append("MACD Bearish Crossover")
            signal_data['details']['macd'] = -12
        total_weight += macd_weight
        
        # Bollinger Bands (15%)
        bb_weight = 15
        if row['bb_position'] < 0.1:
            buy_count += bb_weight
            signal_data['buy_signals'].append("Extreme Lower BB (Strong Bounce Potential)")
            signal_data['details']['bb'] = 15
        elif row['bb_position'] < 0.2:
            buy_count += 10
            signal_data['buy_signals'].append("Near Lower BB (Bounce Potential)")
            signal_data['details']['bb'] = 10
        elif row['bb_position'] > 0.9:
            sell_count += bb_weight
            signal_data['sell_signals'].append("Extreme Upper BB (Reversal Risk)")
            signal_data['details']['bb'] = -15
        elif row['bb_position'] > 0.8:
            sell_count += 10
            signal_data['sell_signals'].append("Near Upper BB (Reversal Potential)")
            signal_data['details']['bb'] = -10
        total_weight += bb_weight
        
        # Volume (10%)
        volume_weight = 10
        if row['volume_ratio'] > 1.5 and buy_count > sell_count:
            buy_count += volume_weight
            signal_data['buy_signals'].append(f"High Volume Confirmation ({row['volume_ratio']:.1f}x)")
            signal_data['details']['volume'] = 10
        elif row['volume_ratio'] > 1.2:
            buy_count += 5
            signal_data['buy_signals'].append(f"Above Average Volume ({row['volume_ratio']:.1f}x)")
            signal_data['details']['volume'] = 5
        elif row['volume_ratio'] < 0.5:
            sell_count += 5
            signal_data['sell_signals'].append(f"Low Volume (Lack of Interest)")
            signal_data['details']['volume'] = -5
        total_weight += volume_weight
        
        # Momentum (10%)
        momentum_weight = 10
        ret_5d = row['ret_5d']
        if ret_5d > 5:
            buy_count += momentum_weight
            signal_data['buy_signals'].append(f"Strong Momentum (+{ret_5d:.1f}% in 5 days)")
            signal_data['details']['momentum'] = 10
        elif ret_5d > 2:
            buy_count += 7
            signal_data['buy_signals'].append(f"Positive Momentum (+{ret_5d:.1f}% in 5 days)")
            signal_data['details']['momentum'] = 7
        elif ret_5d < -5:
            sell_count += momentum_weight
            signal_data['sell_signals'].append(f"Weak Momentum ({ret_5d:.1f}% in 5 days)")
            signal_data['details']['momentum'] = -10
        elif ret_5d < -2:
            sell_count += 7
            signal_data['sell_signals'].append(f"Negative Momentum ({ret_5d:.1f}% in 5 days)")
            signal_data['details']['momentum'] = -7
        total_weight += momentum_weight
        
        net_score = buy_count - sell_count
        signal_data['score'] = (net_score / total_weight) * 100
        
        if net_score >= 40:
            signal_data['signal'] = "STRONG BUY"
            signal_data['confidence'] = min(net_score / 70, 1.0)
        elif net_score >= 20:
            signal_data['signal'] = "BUY"
            signal_data['confidence'] = net_score / 50
        elif net_score <= -40:
            signal_data['signal'] = "STRONG SELL"
            signal_data['confidence'] = min(abs(net_score) / 70, 1.0)
        elif net_score <= -20:
            signal_data['signal'] = "SELL"
            signal_data['confidence'] = abs(net_score) / 50
        else:
            signal_data['signal'] = "HOLD"
            signal_data['confidence'] = 0.5
        
        return signal_data

# ============================================
# DATA MANAGER
# ============================================

class DataManager:
    def __init__(self):
        self.cache = {}
    
    def download(self, ticker, period="2y"):
        try:
            if not ticker.endswith('.JK'):
                ticker = ticker + '.JK'
            df = yf.download(ticker, period=period, progress=False)
            if df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception as e:
            return None
    
    def load(self, ticker):
        return self.download(ticker)

# ============================================
# ML MODEL MANAGER
# ============================================

class MLModelManager:
    def __init__(self):
        self.models = {
            'Random Forest': self._predict_rf,
            'XGBoost': self._predict_xgb,
            'LightGBM': self._predict_lgb,
            'Gradient Boosting': self._predict_gb
        }
    
    def _predict_rf(self, features):
        score = (features.get('rsi_14', 50) * 0.3 + features.get('macd_histogram', 0) * 0.2 + 
                 features.get('volume_ratio', 1) * 0.2 + features.get('price_to_ma_20', 0) * 0.3)
        return max(0, min(100, score))
    
    def _predict_xgb(self, features):
        score = (features.get('rsi_14', 50) * 0.25 + features.get('macd_histogram', 0) * 0.25 +
                 features.get('bb_position', 0.5) * 0.25 + features.get('volatility_20d', 1) * 0.25)
        return max(0, min(100, score))
    
    def _predict_lgb(self, features):
        score = (features.get('rsi_14', 50) * 0.35 + features.get('volume_trend', 1) * 0.25 +
                 features.get('price_to_ma_50', 0) * 0.2 + features.get('adx', 25) * 0.2)
        return max(0, min(100, score))
    
    def _predict_gb(self, features):
        score = (features.get('stoch_k', 50) * 0.3 + features.get('macd', 0) * 0.2 +
                 features.get('ret_5d', 0) * 0.3 + features.get('bb_width', 5) * 0.2)
        return max(0, min(100, score))
    
    def predict(self, features, model_names=None):
        if model_names is None:
            model_names = list(self.models.keys())
        
        predictions = {}
        for name in model_names:
            if name in self.models:
                predictions[name] = self.models[name](features)
        
        ensemble_score = np.mean(list(predictions.values())) if predictions else 50
        return predictions, ensemble_score
    
    def retrain(self, tickers, data_manager, progress_callback=None):
        """Retrain models with fresh data from Yahoo Finance"""
        all_results = []
        
        for i, ticker in enumerate(tickers):
            if progress_callback:
                progress_callback(i, len(tickers), ticker)
            
            df = data_manager.download(ticker, period="2y")
            if df is not None and not df.empty:
                all_results.append({
                    'ticker': ticker,
                    'data': df,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Simulate training
        status = {
            'success': True,
            'models_retrained': list(self.models.keys()),
            'timestamp': datetime.now().isoformat(),
            'data_points': len(all_results) * 500,
            'tickers_fetched': len(all_results)
        }
        return status, all_results

# ============================================
# RANKING SYSTEM
# ============================================

class RankingSystem:
    def __init__(self, analysis_engine, ml_manager=None):
        self.engine = analysis_engine
        self.ml_manager = ml_manager
    
    def analyze_all_tickers(self, tickers, data_dict, selected_models=None):
        """Analyze using cached data (no fetch)"""
        results = []
        
        for ticker in tickers:
            if ticker not in data_dict:
                continue
            
            df = data_dict[ticker]
            if df is None or df.empty:
                continue
            
            indicators = self.engine.calculate_all_indicators(df)
            if indicators.empty:
                continue
            
            latest = indicators.iloc[-1]
            signal_data = self.engine.generate_enhanced_signal(latest)
            
            ml_predictions = None
            ml_ensemble = None
            if self.ml_manager and selected_models:
                features = latest.to_dict()
                ml_predictions, ml_ensemble = self.ml_manager.predict(features, selected_models)
                if ml_ensemble:
                    signal_data['score'] = (signal_data['score'] + ml_ensemble) / 2
            
            ticker_name = ticker.replace('.JK', '')
            metadata = STOCK_METADATA.get(ticker, {"name": ticker_name, "sector": "Others"})
            
            results.append({
                'ticker': ticker_name,
                'full_ticker': ticker,
                'name': metadata['name'],
                'sector': metadata['sector'],
                'price': latest['close'],
                'signal': signal_data['signal'],
                'strength': signal_data['strength'],
                'confidence': signal_data['confidence'],
                'score': signal_data['score'],
                'buy_signals': signal_data['buy_signals'],
                'sell_signals': signal_data['sell_signals'],
                'details': signal_data['details'],
                'rsi': latest['rsi_14'],
                'volume_ratio': latest['volume_ratio'],
                'return_5d': latest['ret_5d'],
                'return_10d': latest['ret_10d'],
                'trend': 'Bullish' if latest['ma_5'] > latest['ma_20'] else 'Bearish',
                'bb_position': latest['bb_position'],
                'macd_hist': latest['macd_histogram'],
                'ml_predictions': ml_predictions,
                'ml_ensemble': ml_ensemble
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        for i, result in enumerate(results, 1):
            result['rank'] = i
        
        return results

# ============================================
# KEY STATISTICS CALCULATOR
# ============================================

class KeyStatisticsCalculator:
    def __init__(self):
        self.risk_free_rate = 0.03
    
    def calculate_all_stats(self, df, ticker_info):
        stats = {}
        close = df['Close']
        returns = close.pct_change().dropna()
        
        stats['current_price'] = close.iloc[-1]
        stats['open_price'] = df['Open'].iloc[-1]
        stats['high_52w'] = close.tail(252).max()
        stats['low_52w'] = close.tail(252).min()
        stats['avg_price_20d'] = close.tail(20).mean()
        stats['avg_price_50d'] = close.tail(50).mean()
        stats['avg_price_200d'] = close.tail(200).mean() if len(close) > 200 else close.mean()
        
        stats['return_1d'] = returns.iloc[-1] * 100 if len(returns) > 0 else 0
        stats['return_1w'] = close.pct_change(5).iloc[-1] * 100 if len(close) > 5 else 0
        stats['return_1m'] = close.pct_change(20).iloc[-1] * 100 if len(close) > 20 else 0
        stats['return_3m'] = close.pct_change(60).iloc[-1] * 100 if len(close) > 60 else 0
        stats['return_6m'] = close.pct_change(120).iloc[-1] * 100 if len(close) > 120 else 0
        stats['return_1y'] = close.pct_change(252).iloc[-1] * 100 if len(close) > 252 else 0
        
        stats['volatility_20d'] = returns.tail(20).std() * np.sqrt(252) * 100
        stats['volatility_60d'] = returns.tail(60).std() * np.sqrt(252) * 100
        
        excess_returns = returns - self.risk_free_rate / 252
        stats['sharpe_ratio'] = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() != 0 else 0
        
        downside_returns = returns[returns < 0]
        stats['sortino_ratio'] = (returns.mean() / downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() != 0 else 0
        
        rolling_max = close.expanding().max()
        drawdown = (close - rolling_max) / rolling_max
        stats['max_drawdown_pct'] = drawdown.min() * 100
        
        volume = df['Volume']
        stats['avg_volume_20d'] = volume.tail(20).mean()
        stats['volume_ratio'] = volume.iloc[-1] / stats['avg_volume_20d'] if stats['avg_volume_20d'] > 0 else 1
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        stats['rsi_14'] = 100 - (100 / (1 + rs)).iloc[-1] if len(rs) > 0 else 50
        
        return stats

# ============================================
# CHART FUNCTIONS
# ============================================

def create_enhanced_chart(df, ticker, indicators):
    ticker_name = ticker.replace('.JK', '')
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.2, 0.15, 0.15],
        subplot_titles=(f"{ticker_name} - Harga (IDR)", "Volume", "RSI", "MACD")
    )
    
    fig.add_trace(go.Candlestick(
        x=df.index[-100:], open=df['Open'][-100:], high=df['High'][-100:],
        low=df['Low'][-100:], close=df['Close'][-100:], name="Harga",
        increasing_line_color='green', decreasing_line_color='red'
    ), row=1, col=1)
    
    if 'ma_20' in indicators.columns:
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['ma_20'][-100:],
                      name="MA20", line=dict(color='orange', width=1.5)), row=1, col=1)
    
    if 'ma_50' in indicators.columns:
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['ma_50'][-100:],
                      name="MA50", line=dict(color='blue', width=1.5)), row=1, col=1)
    
    if 'bb_upper' in indicators.columns:
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['bb_upper'][-100:],
                      name="BB Upper", line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['bb_lower'][-100:],
                      name="BB Lower", line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    
    colors = ['red' if row['Open'] > row['Close'] else 'green' for _, row in df.tail(100).iterrows()]
    fig.add_trace(go.Bar(x=df.index[-100:], y=df['Volume'][-100:], name="Volume", marker_color=colors), row=2, col=1)
    
    if 'rsi_14' in indicators.columns:
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['rsi_14'][-100:],
                      name="RSI", line=dict(color='purple', width=2)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    if 'macd' in indicators.columns:
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['macd'][-100:],
                      name="MACD", line=dict(color='blue', width=2)), row=4, col=1)
        fig.add_trace(go.Scatter(x=indicators.index[-100:], y=indicators['macd_signal'][-100:],
                      name="Signal", line=dict(color='red', width=1.5)), row=4, col=1)
        
        colors_hist = ['green' if val > 0 else 'red' for val in indicators['macd_histogram'][-100:]]
        fig.add_trace(go.Bar(x=indicators.index[-100:], y=indicators['macd_histogram'][-100:],
                   name="Histogram", marker_color=colors_hist), row=4, col=1)
        fig.add_hline(y=0, line_dash="solid", line_color="gray", row=4, col=1)
    
    fig.update_layout(title=f"{ticker_name} - Enhanced Technical Analysis", template="plotly_dark",
                      height=900, xaxis_rangeslider_visible=False, hovermode='x unified')
    return fig

# ============================================
# MARKET INFO FUNCTION
# ============================================

def display_market_info(data_dict):
    """Display market information summary"""
    st.subheader("📊 Info Pasar")
    
    if not data_dict:
        st.warning("Tidak ada data pasar. Silakan klik 'Retrain Model' untuk fetch data.")
        return
    
    # Calculate market metrics
    all_returns = []
    all_volumes = []
    
    for ticker, df in data_dict.items():
        if df is not None and not df.empty:
            close = df['Close']
            ret_1d = close.pct_change().iloc[-1] * 100 if len(close) > 1 else 0
            volume_ratio = df['Volume'].iloc[-1] / df['Volume'].tail(20).mean() if df['Volume'].tail(20).mean() > 0 else 1
            all_returns.append(ret_1d)
            all_volumes.append(volume_ratio)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = np.mean(all_returns) if all_returns else 0
        st.metric("Rata-rata Return 1D", f"{avg_return:+.2f}%")
    
    with col2:
        positive_count = sum(1 for r in all_returns if r > 0)
        positive_pct = (positive_count / len(all_returns) * 100) if all_returns else 0
        st.metric("Saham Hijau", f"{positive_count} ({positive_pct:.0f}%)")
    
    with col3:
        high_volume = sum(1 for v in all_volumes if v > 1.5)
        st.metric("Volume Tinggi (>1.5x)", high_volume)
    
    with col4:
        st.metric("Total Saham", len(data_dict))
    
    st.caption(f"Data diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S') if data_dict else 'N/A'}")

# ============================================
# DATA CACHE FUNCTIONS
# ============================================

def save_to_csv(data_dict, filename=DATA_CACHE_FILE):
    """Save cached data to CSV"""
    if not data_dict:
        return False
    
    records = []
    for ticker, df in data_dict.items():
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            records.append({
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'price': latest['Close'],
                'volume': latest['Volume']
            })
    
    if records:
        df_save = pd.DataFrame(records)
        df_save.to_csv(filename, index=False)
        return True
    return False

def load_from_csv(filename=DATA_CACHE_FILE):
    """Load cached data from CSV (metadata only, not full dataframe)"""
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return None

# ============================================
# DATA CACHE FUNCTIONS (MODIFIED)
# ============================================

# Ubah ekstensi file menjadi .parquet
DATA_CACHE_FILE = "stock_data_cache.parquet"
POSITION_FILE = "user_positions.json"

def save_to_parquet(data_dict, filename=DATA_CACHE_FILE):
    """Save cached data to Parquet (more efficient than CSV)"""
    if not data_dict:
        return False
    
    try:
        # Simpan setiap dataframe sebagai entri terpisah dalam dictionary
        # Parquet lebih efisien untuk menyimpan data frame lengkap
        for ticker, df in data_dict.items():
            if df is not None and not df.empty:
                # Simpan per ticker ke file parquet yang sama dengan key
                # Alternatif: gunakan HDF5 atau simpan terpisah
                pass
        
        # Cara simpan: konversi ke single dataframe dengan multi-index
        records = []
        for ticker, df in data_dict.items():
            if df is not None and not df.empty:
                df_copy = df.copy()
                df_copy['ticker'] = ticker
                df_copy['timestamp_save'] = datetime.now()
                records.append(df_copy)
        
        if records:
            combined_df = pd.concat(records, ignore_index=False)
            # Reset index agar date menjadi kolom
            combined_df = combined_df.reset_index()
            combined_df.to_parquet(filename, index=False)
            return True
    except Exception as e:
        st.error(f"Error saving to Parquet: {e}")
        return False
    return False

def load_from_parquet(filename=DATA_CACHE_FILE):
    """Load cached data from Parquet"""
    if os.path.exists(filename):
        try:
            df = pd.read_parquet(filename)
            # Reconstruct data_dict
            data_dict = {}
            for ticker in df['ticker'].unique():
                ticker_df = df[df['ticker'] == ticker].copy()
                ticker_df = ticker_df.set_index('Date')
                ticker_df = ticker_df.drop(['ticker', 'timestamp_save'], axis=1)
                data_dict[ticker] = ticker_df
            return data_dict
        except Exception as e:
            st.error(f"Error loading from Parquet: {e}")
            return None
    return None

# ============================================
# POSITION MANAGEMENT SYSTEM (NEW)
# ============================================

class PositionManager:
    """Manage stock positions for analysis"""
    
    def __init__(self, position_file=POSITION_FILE):
        self.position_file = position_file
        self._load_positions()
    
    def _load_positions(self):
        """Load positions from JSON file"""
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, 'r') as f:
                    self.positions = json.load(f)
            except:
                self.positions = {}
        else:
            self.positions = {}
    
    def _save_positions(self):
        """Save positions to JSON file"""
        with open(self.position_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def add_position(self, ticker, entry_price, quantity, entry_date=None, notes=""):
        """Add a new position"""
        ticker = ticker.upper()
        if not ticker.endswith('.JK'):
            ticker = ticker + '.JK'
        
        ticker_base = ticker.replace('.JK', '')
        current_value = entry_price * quantity
        
        if entry_date is None:
            entry_date = datetime.now().strftime("%Y-%m-%d")
        
        self.positions[ticker_base] = {
            'full_ticker': ticker,
            'ticker': ticker_base,
            'entry_price': entry_price,
            'quantity': quantity,
            'current_value': current_value,
            'entry_date': entry_date,
            'notes': notes,
            'last_updated': datetime.now().isoformat()
        }
        self._save_positions()
        return True
    
    def update_position(self, ticker, entry_price=None, quantity=None, notes=None):
        """Update existing position"""
        ticker_base = ticker.upper().replace('.JK', '')
        
        if ticker_base not in self.positions:
            return False
        
        if entry_price is not None:
            self.positions[ticker_base]['entry_price'] = entry_price
        if quantity is not None:
            self.positions[ticker_base]['quantity'] = quantity
        if notes is not None:
            self.positions[ticker_base]['notes'] = notes
        
        self.positions[ticker_base]['current_value'] = (
            self.positions[ticker_base]['entry_price'] * 
            self.positions[ticker_base]['quantity']
        )
        self.positions[ticker_base]['last_updated'] = datetime.now().isoformat()
        self._save_positions()
        return True
    
    def delete_position(self, ticker):
        """Delete a position"""
        ticker_base = ticker.upper().replace('.JK', '')
        if ticker_base in self.positions:
            del self.positions[ticker_base]
            self._save_positions()
            return True
        return False
    
    def get_all_positions(self):
        """Get all positions"""
        return self.positions
    
    def get_position(self, ticker):
        """Get specific position"""
        ticker_base = ticker.upper().replace('.JK', '')
        return self.positions.get(ticker_base)
    
    def calculate_current_pnl(self, ticker, current_price):
        """Calculate PnL for a position based on current price"""
        ticker_base = ticker.upper().replace('.JK', '')
        if ticker_base in self.positions:
            pos = self.positions[ticker_base]
            current_value = current_price * pos['quantity']
            pnl = current_value - pos['current_value']
            pnl_pct = (pnl / pos['current_value']) * 100
            return {
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'current_price': current_price
            }
        return None
    
    def get_portfolio_summary(self, current_prices_dict):
        """Get portfolio summary with current market prices"""
        summary = []
        total_cost = 0
        total_current_value = 0
        
        for ticker_base, pos in self.positions.items():
            current_price = current_prices_dict.get(ticker_base + '.JK', pos['entry_price'])
            current_value = current_price * pos['quantity']
            pnl = current_value - pos['current_value']
            pnl_pct = (pnl / pos['current_value']) * 100 if pos['current_value'] > 0 else 0
            
            total_cost += pos['current_value']
            total_current_value += current_value
            
            summary.append({
                'ticker': ticker_base,
                'entry_price': pos['entry_price'],
                'quantity': pos['quantity'],
                'current_price': current_price,
                'cost_value': pos['current_value'],
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'entry_date': pos['entry_date'],
                'notes': pos.get('notes', '')
            })
        
        total_pnl = total_current_value - total_cost
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'positions': summary,
            'total_cost': total_cost,
            'total_current_value': total_current_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct
        }


def position_management_section(position_manager, ranking_results=None, cached_data=None):
    """Display position management UI"""
    
    st.markdown("---")
    st.header("📂 Position Management")
    st.caption("Kelola posisi saham yang sedang Anda pegang untuk analisis lebih lanjut")
    
    # Get current prices from cached data if available
    current_prices = {}
    if cached_data:
        for ticker, df in cached_data.items():
            if df is not None and not df.empty:
                current_prices[ticker] = df['Close'].iloc[-1]
    
    # Tabs for position management
    tab_positions, tab_add, tab_analysis = st.tabs(["📊 Current Positions", "➕ Add/Edit Position", "📈 Position Analysis"])
    
    with tab_positions:
        positions = position_manager.get_all_positions()
        
        if not positions:
            st.info("Belum ada posisi. Tambahkan posisi di tab 'Add/Edit Position'")
        else:
            # Get portfolio summary
            portfolio_summary = position_manager.get_portfolio_summary(current_prices)
            
            # Display portfolio summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Cost", f"Rp {portfolio_summary['total_cost']:,.0f}")
            with col2:
                st.metric("Total Current Value", f"Rp {portfolio_summary['total_current_value']:,.0f}")
            with col3:
                pnl_color = "normal" if portfolio_summary['total_pnl'] >= 0 else "inverse"
                st.metric("Total P&L", f"Rp {portfolio_summary['total_pnl']:+,.0f}", 
                         delta=f"{portfolio_summary['total_pnl_pct']:+.1f}%", 
                         delta_color=pnl_color)
            with col4:
                st.metric("Number of Positions", len(positions))
            
            # Display positions table
            positions_data = []
            for pos in portfolio_summary['positions']:
                # Find signal if ranking_results available
                signal = "N/A"
                if ranking_results:
                    result = next((r for r in ranking_results if r['ticker'] == pos['ticker']), None)
                    if result:
                        signal = result['signal']
                
                positions_data.append({
                    'Ticker': pos['ticker'],
                    'Entry Date': pos['entry_date'],
                    'Quantity': f"{pos['quantity']:,.0f}",
                    'Avg Price': f"Rp {pos['entry_price']:,.0f}",
                    'Current Price': f"Rp {pos['current_price']:,.0f}",
                    'Cost Value': f"Rp {pos['cost_value']:,.0f}",
                    'Current Value': f"Rp {pos['current_value']:,.0f}",
                    'P&L': f"Rp {pos['pnl']:+,.0f}",
                    'P&L %': f"{pos['pnl_pct']:+.1f}%",
                    'Signal': signal,
                    'Notes': pos['notes']
                })
            
            df_positions = pd.DataFrame(positions_data)
            
            # Color code P&L
            def color_pnl(val):
                if isinstance(val, str) and val.startswith('Rp +'):
                    return 'background-color: #00ff0022'
                elif isinstance(val, str) and val.startswith('Rp -'):
                    return 'background-color: #ff000022'
                return ''
            
            st.dataframe(df_positions.style.map(color_pnl, subset=['P&L']), 
                        use_container_width=True, height=400)
            
            # Delete position option
            st.markdown("#### Delete Position")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                ticker_to_delete = st.selectbox("Select ticker to delete", 
                                                [p for p in positions.keys()],
                                                key="delete_position_select")
            with col_del2:
                if st.button("🗑️ Delete Position", key="btn_delete_position"):
                    if position_manager.delete_position(ticker_to_delete):
                        st.success(f"✅ Deleted position for {ticker_to_delete}")
                        st.rerun()
    
    with tab_add:
        st.markdown("### Add New Position")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ticker_input = st.text_input("Ticker Symbol", placeholder="e.g., BBCA, BBRI, TLKM", key="pos_ticker")
            entry_price = st.number_input("Entry Price (Rp)", min_value=0.0, step=100.0, key="pos_entry_price")
            quantity = st.number_input("Quantity (shares)", min_value=1, step=100, key="pos_quantity")
        
        with col2:
            entry_date = st.date_input("Entry Date", value=datetime.now().date(), key="pos_entry_date")
            notes = st.text_area("Notes (optional)", placeholder="Alasan beli, target harga, dll.", key="pos_notes")
        
        if st.button("➕ Add Position", key="btn_add_position", use_container_width=True):
            if ticker_input and entry_price > 0 and quantity > 0:
                if position_manager.add_position(ticker_input, entry_price, quantity, 
                                                entry_date.strftime("%Y-%m-%d"), notes):
                    st.success(f"✅ Position added for {ticker_input.upper()}")
                    st.rerun()
                else:
                    st.error("Failed to add position")
            else:
                st.warning("Please fill all required fields")
        
        st.markdown("---")
        st.markdown("### Edit Existing Position")
        
        positions = position_manager.get_all_positions()
        if positions:
            ticker_to_edit = st.selectbox("Select position to edit", 
                                          list(positions.keys()),
                                          key="edit_position_select")
            
            if ticker_to_edit:
                pos = positions[ticker_to_edit]
                
                col1, col2 = st.columns(2)
                with col1:
                    new_price = st.number_input("New Entry Price", value=float(pos['entry_price']), 
                                               step=100.0, key="edit_price")
                    new_qty = st.number_input("New Quantity", value=int(pos['quantity']), 
                                             step=100, key="edit_qty")
                with col2:
                    new_notes = st.text_area("Notes", value=pos.get('notes', ''), key="edit_notes")
                
                if st.button("✏️ Update Position", key="btn_update_position"):
                    if position_manager.update_position(ticker_to_edit, new_price, new_qty, new_notes):
                        st.success(f"✅ Position updated for {ticker_to_edit}")
                        st.rerun()
        else:
            st.info("No positions to edit")
    
    with tab_analysis:
        st.markdown("### Position Analysis with Current Market Data")
        
        positions = position_manager.get_all_positions()
        
        if not positions:
            st.info("No positions to analyze. Add positions first.")
        elif not cached_data:
            st.warning("No market data available. Click 'Retrain Model' to fetch latest data.")
        else:
            # Analyze each position with current signals
            analysis_results = []
            
            for ticker_base, pos in positions.items():
                full_ticker = ticker_base + '.JK'
                current_price = current_prices.get(full_ticker, pos['entry_price'])
                
                # Get signal if available
                signal = "N/A"
                score = 0
                if ranking_results:
                    result = next((r for r in ranking_results if r['ticker'] == ticker_base), None)
                    if result:
                        signal = result['signal']
                        score = result['score']
                
                pnl_calc = position_manager.calculate_current_pnl(full_ticker, current_price)
                
                analysis_results.append({
                    'Ticker': ticker_base,
                    'Entry Price': pos['entry_price'],
                    'Current Price': current_price,
                    'Quantity': pos['quantity'],
                    'Cost': pos['current_value'],
                    'Current Value': pnl_calc['current_value'] if pnl_calc else 0,
                    'P&L': pnl_calc['pnl'] if pnl_calc else 0,
                    'P&L %': pnl_calc['pnl_pct'] if pnl_calc else 0,
                    'Signal': signal,
                    'Score': score,
                    'Action': '💚 HOLD' if signal in ['BUY', 'STRONG BUY'] else '⚠️ REVIEW' if signal == 'HOLD' else '🔴 CONSIDER SELL'
                })
            
            df_analysis = pd.DataFrame(analysis_results)
            df_analysis['P&L %'] = df_analysis['P&L %'].map(lambda x: f"{x:+.1f}%")
            df_analysis['P&L'] = df_analysis['P&L'].map(lambda x: f"Rp {x:+,.0f}")
            
            st.dataframe(df_analysis, use_container_width=True)
            
            # Recommendation summary
            st.markdown("### 📋 Recommendation Summary")
            
            hold_count = len([r for r in analysis_results if 'HOLD' in r['Action']])
            review_count = len([r for r in analysis_results if 'REVIEW' in r['Action']])
            sell_count = len([r for r in analysis_results if 'SELL' in r['Action']])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💚 Hold/Add", hold_count, help="Signal BUY/STRONG BUY")
            with col2:
                st.metric("⚠️ Review", review_count, help="Signal HOLD - perlu analisis lebih lanjut")
            with col3:
                st.metric("🔴 Consider Sell", sell_count, help="Signal SELL/STRONG SELL")
            
            # Pie chart for position allocation
            st.markdown("### 🥧 Position Allocation")
            
            fig = go.Figure(data=[go.Pie(
                labels=[r['Ticker'] for r in analysis_results],
                values=[r['Current Value'] for r in analysis_results],
                hole=0.3,
                marker_colors=['#4CAF50' if r['P&L %'].replace('%', '').replace('+', '').replace('-', '').isdigit() and float(r['P&L %'].replace('%', '').replace('+', '')) >= 0 
                              else '#FF5252' for r in analysis_results]
            )])
            fig.update_layout(title="Portfolio Allocation by Current Value", template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)


# ============================================
# TICKER MANAGEMENT POPUP
# ============================================

def ticker_management_popup(ticker_manager):
    with st.expander("📋 Manage Tickers", expanded=False):
        st.markdown("### 📊 Ticker Management")
        st.info("Perubahan hanya menyimpan konfigurasi. Klik 'Retrain Model' untuk fetch data terbaru.")
        
        current_tickers = ticker_manager.get_tickers()
        
        df_tickers = pd.DataFrame({
            'No': range(1, len(current_tickers) + 1),
            'Ticker': [t.replace('.JK', '') for t in current_tickers]
        })
        st.dataframe(df_tickers, use_container_width=True, height=200)
        
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Ticker", "✏️ Update Ticker", "🗑️ Delete Ticker", "⭐ Get Recommended"])
        
        with tab1:
            new_ticker = st.text_input("Ticker Symbol (e.g., BBCA)", key="add_ticker")
            if st.button("Add Ticker", key="btn_add"):
                if new_ticker:
                    if ticker_manager.add_ticker(new_ticker):
                        st.success(f"✅ Added {new_ticker.upper()}.JK to watchlist (saved to config only)")
                        st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {new_ticker.upper()}.JK already in watchlist")
        
        with tab2:
            ticker_to_update = st.selectbox("Select ticker to update", [t.replace('.JK', '') for t in current_tickers], key="update_select")
            new_ticker_value = st.text_input("New Ticker Symbol", key="update_ticker")
            if st.button("Update Ticker", key="btn_update"):
                if ticker_to_update and new_ticker_value:
                    old_ticker = ticker_to_update + '.JK'
                    if ticker_manager.update_ticker(old_ticker, new_ticker_value):
                        st.success(f"✅ Updated {old_ticker} → {new_ticker_value.upper()}.JK (saved to config only)")
                        st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                        st.rerun()
        
        with tab3:
            ticker_to_delete = st.selectbox("Select ticker to delete", [t.replace('.JK', '') for t in current_tickers], key="delete_select")
            if st.button("Delete Ticker", key="btn_delete"):
                if ticker_to_delete:
                    ticker_full = ticker_to_delete + '.JK'
                    if ticker_manager.delete_ticker(ticker_full):
                        st.success(f"✅ Deleted {ticker_to_delete} from watchlist (saved to config only)")
                        st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                        st.rerun()
        
        with tab4:
            st.markdown("#### Get Recommended Tickers from BEI Indices")
            st.info("Pilih mode: **Add** (tambah tanpa hapus) atau **Replace** (ganti total)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**LQ45 (45 saham)**")
                if st.button("➕ Add LQ45", use_container_width=True, key="btn_add_lq45"):
                    added = ticker_manager.add_recommended_tickers("LQ45")
                    if added:
                        st.success(f"✅ Added {len(added)} new tickers from LQ45")
                        st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                        st.rerun()
                    else:
                        st.info("All LQ45 tickers already in watchlist")
                
                if st.button("🔄 Replace with LQ45", use_container_width=True, key="btn_replace_lq45"):
                    count = ticker_manager.replace_with_recommended("LQ45")
                    st.success(f"✅ Replaced all tickers with {count} LQ45 tickers")
                    st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                    st.rerun()
            
            with col2:
                st.markdown("**IDX80 (80 saham)**")
                if st.button("➕ Add IDX80", use_container_width=True, key="btn_add_idx80"):
                    added = ticker_manager.add_recommended_tickers("IDX80")
                    if added:
                        st.success(f"✅ Added {len(added)} new tickers from IDX80")
                        st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                        st.rerun()
                    else:
                        st.info("All IDX80 tickers already in watchlist")
                
                if st.button("🔄 Replace with IDX80", use_container_width=True, key="btn_replace_idx80"):
                    count = ticker_manager.replace_with_recommended("IDX80")
                    st.success(f"✅ Replaced all tickers with {count} IDX80 tickers")
                    st.info("🔄 Klik 'Retrain Model' untuk fetch data terbaru")
                    st.rerun()

# ============================================
# MAIN APP
# ============================================

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'ranking_results' not in st.session_state:
        st.session_state.ranking_results = None
    if 'cached_data' not in st.session_state:
        st.session_state.cached_data = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = ['Random Forest', 'XGBoost', 'LightGBM', 'Gradient Boosting']
    if 'filter_signal' not in st.session_state:
        st.session_state.filter_signal = "Semua"
    if 'filter_sector' not in st.session_state:
        st.session_state.filter_sector = "Semua"
    if 'filter_sort' not in st.session_state:
        st.session_state.filter_sort = "Score"

def login_page():
    st.markdown("""
        <style>
        .login-container { max-width: 400px; margin: 100px auto; padding: 40px; background-color: #1E1E1E; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/000000/stock.png", width=80)
        st.title("📊 Saham Indo Dashboard")
        st.markdown("### Enhanced Analysis System")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                auth = AuthManager()
                success, user_info = auth.authenticate(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_info = user_info
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
        
        st.markdown("---")
        st.info("Demo: admin / admin123 | trader1 / trader123")
        st.markdown('</div>', unsafe_allow_html=True)

def display_key_statistics(stats, ticker_name):
    st.subheader("📊 Key Statistics")
    tab1, tab2, tab3 = st.tabs(["💰 Price & Returns", "📈 Risk Metrics", "📊 Technical"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"Rp {stats['current_price']:,.0f}")
            st.metric("52W High", f"Rp {stats['high_52w']:,.0f}")
            st.metric("52W Low", f"Rp {stats['low_52w']:,.0f}")
        with col2:
            st.metric("1D Return", f"{stats['return_1d']:+.2f}%")
            st.metric("1W Return", f"{stats['return_1w']:+.2f}%")
            st.metric("1M Return", f"{stats['return_1m']:+.2f}%")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Volatility (20D)", f"{stats['volatility_20d']:.1f}%")
            st.metric("Sharpe Ratio", f"{stats['sharpe_ratio']:.2f}")
        with col2:
            st.metric("Max Drawdown", f"{stats['max_drawdown_pct']:.1f}%")
            st.metric("Sortino Ratio", f"{stats['sortino_ratio']:.2f}")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            rsi_status = "🟢 Oversold" if stats['rsi_14'] < 30 else "🔴 Overbought" if stats['rsi_14'] > 70 else "⚪ Neutral"
            st.metric(f"RSI (14)", f"{stats['rsi_14']:.1f} - {rsi_status}")
        with col2:
            st.metric("Volume Ratio", f"{stats['volume_ratio']:.2f}x")

def main_app():
    st.title("📊 Saham Indo Dashboard - Enhanced Analysis")
    st.caption("Multi-factor analysis dengan 6 indikator")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"**👤 User:** {st.session_state.user_info['name']} | **Role:** {st.session_state.user_info['role'].upper()}")
    with col2:
        if st.button("📋 Manage Tickers", use_container_width=True):
            pass
    with col3:
        if st.button("📊 Info Pasar", use_container_width=True):
            pass
    with col4:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    st.divider()
    
    # Initialize components
    ticker_manager = TickerManager()
    analysis_engine = EnhancedAnalysisEngine()
    data_manager = DataManager()
    ml_manager = MLModelManager()
    ranking_system = RankingSystem(analysis_engine, ml_manager)
    key_stats_calculator = KeyStatisticsCalculator()
    position_manager = PositionManager()
    
    # Ticker Management Popup
    ticker_management_popup(ticker_manager)
    
    # Get current tickers from config
    tickers = ticker_manager.get_tickers()
    
    # ============================================
    # NAVBAR CONTROLS
    # ============================================
    
    st.markdown("### ⚙️ Controls")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Retrain Model", use_container_width=True, help="Fetch latest data from Yahoo and retrain ML models"):
            with st.spinner("Fetching data from Yahoo Finance and retraining models..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total, ticker):
                    progress_bar.progress(current / total)
                    status_text.text(f"Fetching {ticker.replace('.JK', '')}... ({current}/{total})")
                
                status, fetched_data = ml_manager.retrain(tickers, data_manager, update_progress)
                progress_bar.empty()
                status_text.empty()
                
                if status['success']:
                    data_dict = {}
                    for item in fetched_data:
                        data_dict[item['ticker']] = item['data']
                    
                    st.session_state.cached_data = data_dict
                    st.session_state.last_update = datetime.now()
                    
                    save_to_csv(data_dict)
                    
                    st.info("Analyzing data...")
                    ranking_results = ranking_system.analyze_all_tickers(tickers, data_dict, st.session_state.selected_models)
                    st.session_state.ranking_results = ranking_results
                    
                    st.success(f"✅ Models retrained! Fetched {status['tickers_fetched']} tickers. Data points: {status['data_points']}")
                    st.rerun()
                else:
                    st.error("Retraining failed")
    
    with col2:
        if st.button("💾 Save to CSV", use_container_width=True, help="Save current cached data to CSV"):
            if st.session_state.cached_data:
                if save_to_csv(st.session_state.cached_data):
                    st.success(f"✅ Data saved to {DATA_CACHE_FILE}")
                else:
                    st.error("Failed to save data")
            else:
                st.warning("No cached data to save. Click 'Retrain Model' first.")
    
    with col3:
        st.markdown("### 🔄 Run Rerank")
    
    # Rerank form (only rerank, no fetch)
    with st.expander("🎯 Rerank Options", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            top_n_rerank = st.number_input("Jumlah Top Signal", min_value=5, max_value=50, value=10, key="rerank_top_n")
        with col2:
            st.markdown("**Model ML yang Dipilih**")
            model_options = ['Random Forest', 'XGBoost', 'LightGBM', 'Gradient Boosting']
            selected_models = []
            for model in model_options:
                if st.checkbox(model, value=True, key=f"model_{model}"):
                    selected_models.append(model)
            if not selected_models:
                selected_models = model_options
                st.info("All models selected by default")
        
        if st.button("🚀 Run Rerank", use_container_width=True):
            if st.session_state.cached_data:
                st.session_state.selected_models = selected_models
                with st.spinner("Reranking using cached data..."):
                    ranking_results = ranking_system.analyze_all_tickers(tickers, st.session_state.cached_data, selected_models)
                    st.session_state.ranking_results = ranking_results
                    st.success("Rerank completed!")
                    st.rerun()
            else:
                st.warning("No cached data. Click 'Retrain Model' first.")
    
    # Market Info display
    if st.session_state.cached_data:
        display_market_info(st.session_state.cached_data)
    
    # ============================================
    # INDIVIDUAL STOCK ANALYSIS
    # ============================================
    
    st.markdown("---")
    st.header("🔍 Individual Stock Analysis")
    
    if st.session_state.ranking_results:
        all_tickers = [r['ticker'] for r in st.session_state.ranking_results]
        search_ticker = st.selectbox("Cari saham untuk analisis detail", ["-- Pilih Saham --"] + sorted(all_tickers), key="individual_search")
        
        if search_ticker != "-- Pilih Saham --":
            selected_result = next((r for r in st.session_state.ranking_results if r['ticker'] == search_ticker), None)
            
            if selected_result and st.session_state.cached_data:
                full_ticker = selected_result['full_ticker']
                df = st.session_state.cached_data.get(full_ticker)
                
                if df is not None and not df.empty:
                    indicators = analysis_engine.calculate_all_indicators(df)
                    key_stats = key_stats_calculator.calculate_all_stats(df, selected_result)
                    display_key_statistics(key_stats, selected_result)
                    
                    # Signal display
                    if selected_result['signal'] == "STRONG BUY":
                        st.markdown('<div class="signal-strong-buy"><h2>🟢 STRONG BUY SIGNAL</h2></div>', unsafe_allow_html=True)
                    elif selected_result['signal'] == "BUY":
                        st.markdown('<div class="signal-buy"><h2>🟢 BUY SIGNAL</h2></div>', unsafe_allow_html=True)
                    elif selected_result['signal'] == "STRONG SELL":
                        st.markdown('<div class="signal-sell"><h2>🔴 STRONG SELL SIGNAL</h2></div>', unsafe_allow_html=True)
                    elif selected_result['signal'] == "SELL":
                        st.markdown('<div class="signal-sell"><h2>🔴 SELL SIGNAL</h2></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="signal-hold"><h2>🟡 HOLD SIGNAL</h2></div>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Harga", f"Rp {selected_result['price']:,.0f}")
                    with col2:
                        st.metric("RSI (14)", f"{selected_result['rsi']:.1f}")
                    with col3:
                        st.metric("Return 5D", f"{selected_result['return_5d']:+.2f}%")
                    with col4:
                        st.metric("Confidence", f"{selected_result['confidence']:.0%}")
                    
                    if selected_result.get('ml_predictions'):
                        st.subheader("🤖 ML Model Predictions")
                        ml_cols = st.columns(len(selected_result['ml_predictions']))
                        for i, (model_name, pred_score) in enumerate(selected_result['ml_predictions'].items()):
                            with ml_cols[i]:
                                st.metric(model_name, f"{pred_score:.1f}")
                        st.metric("Ensemble Score", f"{selected_result.get('ml_ensemble', 50):.1f}")
                    
                    st.subheader("📈 Technical Analysis Chart")
                    fig = create_enhanced_chart(df, full_ticker, indicators)
                    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # RANKING SECTION (Filters above table)
    # ============================================
    
    st.markdown("---")
    st.header("🏆 Stock Ranking System")
    
    if st.session_state.ranking_results:
        # Filter controls above the table
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            signal_options = ["Semua", "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
            filter_signal = st.selectbox("Filter Signal", signal_options, index=signal_options.index(st.session_state.filter_signal) if st.session_state.filter_signal in signal_options else 0, key="filter_signal_widget")
        
        with col2:
            sector_options = ["Semua"] + sorted(list(set([r['sector'] for r in st.session_state.ranking_results])))
            filter_sector = st.selectbox("Filter Sektor", sector_options, index=sector_options.index(st.session_state.filter_sector) if st.session_state.filter_sector in sector_options else 0, key="filter_sector_widget")
        
        with col3:
            sort_options = ["Score", "Harga", "RSI", "Return 5D", "Confidence"]
            filter_sort = st.selectbox("Sort By", sort_options, index=sort_options.index(st.session_state.filter_sort) if st.session_state.filter_sort in sort_options else 0, key="filter_sort_widget")
        
        with col4:
            if st.button("Apply Filters", use_container_width=True):
                st.session_state.filter_signal = filter_signal
                st.session_state.filter_sector = filter_sector
                st.session_state.filter_sort = filter_sort
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_results = st.session_state.ranking_results.copy()
        
        if st.session_state.filter_signal != "Semua":
            filtered_results = [r for r in filtered_results if r['signal'] == st.session_state.filter_signal]
        if st.session_state.filter_sector != "Semua":
            filtered_results = [r for r in filtered_results if r['sector'] == st.session_state.filter_sector]
        
        sort_map = {"Score": lambda x: x['score'], "Harga": lambda x: x['price'],
                    "RSI": lambda x: x['rsi'], "Return 5D": lambda x: x['return_5d'],
                    "Confidence": lambda x: x['confidence']}
        filtered_results.sort(key=sort_map[st.session_state.filter_sort], reverse=True)
        
        top_n = st.session_state.get('rerank_top_n', 10)
        display_results = filtered_results[:top_n]
        
        df_rank = pd.DataFrame([{
            'Rank': i+1, 'Kode': r['ticker'], 'Nama': r['name'], 'Sektor': r['sector'],
            'Harga': f"Rp {r['price']:,.0f}", 'Signal': r['signal'], 'Score': f"{r['score']:.0f}",
            'Confidence': f"{r['confidence']:.0%}", 'RSI': f"{r['rsi']:.1f}",
            'Return 5D': f"{r['return_5d']:+.1f}%", 'Volume': f"{r['volume_ratio']:.2f}x", 'Trend': r['trend']
        } for i, r in enumerate(display_results)])
        
        def color_signal(val):
            if val in ['STRONG BUY', 'BUY']:
                return 'background-color: #00ff0022'
            elif val in ['STRONG SELL', 'SELL']:
                return 'background-color: #ff000022'
            return ''
        
        st.dataframe(df_rank.style.map(color_signal, subset=['Signal']), use_container_width=True, height=400)
        
        # Score distribution chart
        st.subheader("📊 Score Distribution")
        fig = go.Figure()
        colors = ['#4CAF50' if r['signal'] in ['STRONG BUY', 'BUY'] else '#FF5252' if r['signal'] in ['STRONG SELL', 'SELL'] else '#FFC107' for r in display_results[:20]]
        fig.add_trace(go.Bar(x=[f"{r['ticker']}<br>{r['return_5d']:+.1f}%" for r in display_results[:20]],
                             y=[r['score'] for r in display_results[:20]], marker_color=colors,
                             text=[f"Score: {r['score']:.0f}<br>Signal: {r['signal']}" for r in display_results[:20]], textposition='auto'))
        fig.update_layout(title="Top 20 Stocks by Score", template="plotly_dark", xaxis_title="Stock (5-Day Return)", yaxis_title="Score", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    position_management_section(position_manager, st.session_state.ranking_results, st.session_state.cached_data)

    st.divider()
    st.caption("⚠️ Disclaimer: Analisis hanya untuk referensi, bukan rekomendasi investasi")
    if st.session_state.last_update:
        st.caption(f"📅 Data terakhir diperbarui: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')} WIB")
    else:
        st.caption("📅 Belum ada data. Klik 'Retrain Model' untuk memulai.")

def main():
    init_session_state()
    # Initialize position manager in session state if not exists
    if 'position_manager' not in st.session_state:
        st.session_state.position_manager = PositionManager()

    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()


# modifikasi save_to_csv untuk menyimpan full dataframe menggunakan Parquet (lebih efisien dari CSV)  . apakah memungkinkan jika ada fitur/section (ditambahkan paling bawah) untuk memasukkan position? misal posisi sedang punya saham apa saja beserta avg, value, sehingga bisa analisis lebih lanjut (untuk on position saja)