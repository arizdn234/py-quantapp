import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
import hashlib
import hmac
from functools import wraps

# Page config
st.set_page_config(
    page_title="Saham Indo Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================
# AUTHENTICATION SYSTEM
# ============================================

class AuthManager:
    """User authentication and session management"""
    
    def __init__(self, user_file="users.json"):
        self.user_file = user_file
        self._init_user_file()
    
    def _init_user_file(self):
        """Initialize user file with default admin if not exists"""
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
                },
                "analyst": {
                    "password": hashlib.sha256("analyst123".encode()).hexdigest(),
                    "name": "Market Analyst",
                    "email": "analyst@example.com",
                    "role": "analyst",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                }
            }
            with open(self.user_file, "w") as f:
                json.dump(default_users, f, indent=2)
    
    def authenticate(self, username, password):
        """Authenticate user"""
        try:
            with open(self.user_file, "r") as f:
                users = json.load(f)
            
            if username in users:
                hashed = hashlib.sha256(password.encode()).hexdigest()
                if hmac.compare_digest(hashed, users[username]["password"]):
                    # Update last login
                    users[username]["last_login"] = datetime.now().isoformat()
                    with open(self.user_file, "w") as f:
                        json.dump(users, f, indent=2)
                    return True, users[username]
            return False, None
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return False, None
    
    def register_user(self, username, password, name, email, role="user"):
        """Register new user"""
        try:
            with open(self.user_file, "r") as f:
                users = json.load(f)
            
            if username in users:
                return False, "Username already exists"
            
            users[username] = {
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "name": name,
                "email": email,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
            
            with open(self.user_file, "w") as f:
                json.dump(users, f, indent=2)
            
            return True, "User registered successfully"
        except Exception as e:
            return False, f"Registration error: {e}"
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        try:
            with open(self.user_file, "r") as f:
                users = json.load(f)
            
            if username in users:
                old_hashed = hashlib.sha256(old_password.encode()).hexdigest()
                if hmac.compare_digest(old_hashed, users[username]["password"]):
                    users[username]["password"] = hashlib.sha256(new_password.encode()).hexdigest()
                    with open(self.user_file, "w") as f:
                        json.dump(users, f, indent=2)
                    return True, "Password changed successfully"
                return False, "Incorrect old password"
            return False, "User not found"
        except Exception as e:
            return False, f"Error: {e}"

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()

# Login page
def login_page():
    """Display login page"""
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 40px;
            background-color: #1E1E1E;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-button {
            width: 100%;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/000000/stock.png", width=80)
        st.title("📊 Saham Indo Dashboard")
        st.markdown("### Login")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    auth = AuthManager()
                    success, user_info = auth.authenticate(username, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_info = user_info
                        st.session_state.last_activity = datetime.now()
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
                else:
                    st.warning("⚠️ Harap isi username dan password!")
        
        # Register section
        st.markdown("---")
        st.markdown("### Belum punya akun?")
        
        with st.expander("Daftar Akun Baru"):
            with st.form("register_form"):
                new_username = st.text_input("Username", key="reg_username")
                new_password = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Konfirmasi Password", type="password")
                new_name = st.text_input("Nama Lengkap")
                new_email = st.text_input("Email")
                
                register_submit = st.form_submit_button("Daftar")
                
                if register_submit:
                    if new_password != confirm_password:
                        st.error("Password dan konfirmasi password tidak cocok!")
                    elif len(new_password) < 6:
                        st.error("Password minimal 6 karakter!")
                    else:
                        auth = AuthManager()
                        success, message = auth.register_user(
                            new_username, new_password, new_name, new_email, "user"
                        )
                        if success:
                            st.success("✅ Registrasi berhasil! Silakan login.")
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Demo credentials
        st.markdown("---")
        st.markdown("### Demo Credentials:")
        st.code("""
        Admin: admin / admin123
        Trader: trader1 / trader123
        Analyst: analyst / analyst123
        """)

# Logout function
def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.rerun()

# ============================================
# STOCKBIT PRICE ADJUSTMENT
# ============================================

class StockbitPriceAdjuster:
    """Adjust prices to match Stockbit standards (per lot = 100 shares)"""
    
    def __init__(self):
        self.lot_size = 100  # 1 lot = 100 saham
        self.price_adjustment_factor = {}
        
    def adjust_to_stockbit(self, df, ticker):
        """Adjust Yahoo Finance prices to match Stockbit"""
        if df is None or df.empty:
            return df
        
        # Stockbit reference prices (simulated - in production, use actual API)
        stockbit_prices = {
            'BBCA.JK': 9750,
            'BBRI.JK': 4950,
            'BMRI.JK': 6250,
            'TLKM.JK': 3850,
            'ASII.JK': 5250,
            'UNVR.JK': 3850,
            'ADRO.JK': 2450,
            'ICBP.JK': 10250,
            'INDF.JK': 6850,
            'GOTO.JK': 98,
            'SMGR.JK': 4850,
            'INCO.JK': 4250,
            'ANTM.JK': 1850,
            'CPIN.JK': 4950,
            'PGAS.JK': 1250
        }
        
        # Get latest Yahoo price
        yahoo_latest = df['Close'].iloc[-1]
        
        # Get Stockbit reference price
        stockbit_price = stockbit_prices.get(ticker, yahoo_latest * 1.02)  # Default +2%
        
        # Calculate adjustment factor
        if yahoo_latest > 0:
            adjustment_factor = stockbit_price / yahoo_latest
            self.price_adjustment_factor[ticker] = adjustment_factor
            
            # Apply adjustment to all prices
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df.columns:
                    df[col] = df[col] * adjustment_factor
        
        return df
    
    def calculate_lot_value(self, price):
        """Calculate value per lot (100 shares)"""
        return price * self.lot_size
    
    def format_stockbit_price(self, price):
        """Format price in Stockbit style"""
        return f"Rp {price:,.0f}"

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
    <style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
    }
    .signal-buy {
        background-color: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00ff00;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .signal-sell {
        background-color: rgba(255, 0, 0, 0.1);
        border-left: 4px solid #ff0000;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .signal-hold {
        background-color: rgba(255, 255, 0, 0.1);
        border-left: 4px solid #ffff00;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .user-info {
        background-color: #2E2E2E;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stockbit-note {
        background-color: #1E3A3A;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
        margin: 10px 0;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INDONESIAN STOCK MARKET INFO
# ============================================

IDX_INFO = {
    "trading_hours": "09:00 - 15:00 WIB",
    "currency": "IDR",
    "exchange": "Indonesia Stock Exchange (IDX)",
    "suffix": ".JK",
    "lot_size": 100  # 1 lot = 100 saham
}

# Popular Indonesian stocks
DEFAULT_TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK",
    "UNVR.JK", "ADRO.JK", "ICBP.JK", "INDF.JK", "GOTO.JK"
]

# ============================================
# TICKER MANAGER
# ============================================

class TickerManager:
    def __init__(self, filename="tickers_idn.json"):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(DEFAULT_TICKERS, f)
    
    def load(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_TICKERS
    
    def save(self, tickers):
        with open(self.filename, "w") as f:
            json.dump(tickers, f, indent=2)
    
    def add(self, ticker):
        tickers = self.load()
        if not ticker.endswith('.JK'):
            ticker = ticker + '.JK'
        if ticker not in tickers:
            tickers.append(ticker)
            self.save(tickers)
            return True
        return False
    
    def remove(self, ticker):
        tickers = self.load()
        if ticker in tickers:
            tickers.remove(ticker)
            self.save(tickers)
            return True
        return False

# ============================================
# DATA MANAGER WITH STOCKBIT ADJUSTMENT
# ============================================

class DataManager:
    def __init__(self):
        self.cache = {}
        self.price_adjuster = StockbitPriceAdjuster()
    
    def download(self, ticker, period="2y"):
        try:
            if not ticker.endswith('.JK'):
                ticker = ticker + '.JK'
            
            df = yf.download(ticker, period=period, progress=False)
            if df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Adjust to Stockbit prices
            df = self.price_adjuster.adjust_to_stockbit(df, ticker)
            
            # Add ticker info
            df['Ticker'] = ticker.replace('.JK', '')
            
            return df
        except Exception as e:
            return None
    
    def load(self, ticker):
        return self.download(ticker)

# ============================================
# FEATURE ENGINEERING
# ============================================

class FeatureEngineer:
    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        exp_fast = prices.ewm(span=fast, adjust=False).mean()
        exp_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = exp_fast - exp_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper = rolling_mean + (rolling_std * num_std)
        lower = rolling_mean - (rolling_std * num_std)
        return upper, rolling_mean, lower
    
    def transform(self, df):
        feat = pd.DataFrame(index=df.index)
        
        feat["Close"] = df["Close"]
        feat["Open"] = df["Open"]
        feat["High"] = df["High"]
        feat["Low"] = df["Low"]
        feat["Volume"] = df["Volume"]
        
        # Returns
        feat["ret1"] = df["Close"].pct_change()
        feat["ret5"] = df["Close"].pct_change(5)
        feat["ret20"] = df["Close"].pct_change(20)
        
        # Moving averages
        feat["ma20"] = df["Close"].rolling(window=20).mean()
        feat["ma50"] = df["Close"].rolling(window=50).mean()
        feat["ma200"] = df["Close"].rolling(window=200).mean()
        
        # Price relative to MAs
        feat["price_to_ma20"] = (df["Close"] / feat["ma20"] - 1) * 100
        feat["price_to_ma50"] = (df["Close"] / feat["ma50"] - 1) * 100
        
        # RSI
        feat["rsi"] = self.calculate_rsi(df["Close"])
        
        # MACD
        macd, macd_signal, macd_hist = self.calculate_macd(df["Close"])
        feat["macd"] = macd
        feat["macd_signal"] = macd_signal
        feat["macd_histogram"] = macd_hist
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df["Close"])
        feat["bb_upper"] = bb_upper
        feat["bb_middle"] = bb_middle
        feat["bb_lower"] = bb_lower
        feat["bb_width"] = ((bb_upper - bb_lower) / bb_middle) * 100
        feat["bb_position"] = (df["Close"] - bb_lower) / (bb_upper - bb_lower)
        
        # Volume analysis
        feat["volume_ma"] = df["Volume"].rolling(window=20).mean()
        feat["volume_ratio"] = df["Volume"] / feat["volume_ma"]
        feat["volume_trend"] = df["Volume"].rolling(5).mean() / df["Volume"].rolling(20).mean()
        
        # Volatility
        feat["volatility"] = feat["ret1"].rolling(window=20).std() * 100
        
        # Support/Resistance
        feat["support"] = df["Low"].rolling(window=20).min()
        feat["resistance"] = df["High"].rolling(window=20).max()
        
        return feat.dropna()

# ============================================
# SIGNAL GENERATOR
# ============================================

class SignalGenerator:
    def __init__(self):
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.volume_threshold = 1.5
    
    def generate_signal(self, row):
        if pd.isna(row["ma20"]) or pd.isna(row["ma50"]):
            return "HOLD", 0, []
        
        reasons = []
        buy_score = 0
        sell_score = 0
        
        # Trend analysis
        if row["ma20"] > row["ma50"]:
            if row["ma50"] > row["ma200"] if "ma200" in row else False:
                buy_score += 3
                reasons.append("Strong Uptrend (Golden Cross)")
            else:
                buy_score += 2
                reasons.append("Bullish Trend")
        else:
            if row["ma20"] < row["ma50"] and row["ma50"] < row["ma200"] if "ma200" in row else False:
                sell_score += 3
                reasons.append("Strong Downtrend (Death Cross)")
            else:
                sell_score += 2
                reasons.append("Bearish Trend")
        
        # RSI momentum
        if row["rsi"] < self.rsi_oversold:
            buy_score += 2
            reasons.append(f"Oversold (RSI: {row['rsi']:.1f})")
        elif row["rsi"] > self.rsi_overbought:
            sell_score += 2
            reasons.append(f"Overbought (RSI: {row['rsi']:.1f})")
        
        # MACD momentum
        if row["macd"] > row["macd_signal"]:
            if row["macd_histogram"] > 0:
                buy_score += 2
                reasons.append("MACD Bullish Crossover")
            else:
                buy_score += 1
                reasons.append("MACD Positive")
        else:
            if row["macd_histogram"] < 0:
                sell_score += 2
                reasons.append("MACD Bearish Crossover")
            else:
                sell_score += 1
                reasons.append("MACD Negative")
        
        # Bollinger Bands
        if row["bb_position"] < 0.2:
            buy_score += 1
            reasons.append("Near Lower BB (Potential Bounce)")
        elif row["bb_position"] > 0.8:
            sell_score += 1
            reasons.append("Near Upper BB (Potential Reversal)")
        
        # Volume confirmation
        if row["volume_ratio"] > self.volume_threshold:
            if buy_score > sell_score:
                buy_score += 1
                reasons.append("High Volume Confirmation")
            elif sell_score > buy_score:
                sell_score += 1
                reasons.append("High Volume Distribution")
        
        # Price action
        if row["price_to_ma20"] > 5:
            sell_score += 1
            reasons.append("Extended above MA20")
        elif row["price_to_ma20"] < -5:
            buy_score += 1
            reasons.append("Near MA20 Support")
        
        # Determine signal
        if buy_score >= 4:
            signal = "BUY"
            confidence = min(buy_score / 8, 1.0)
        elif sell_score >= 4:
            signal = "SELL"
            confidence = min(sell_score / 8, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return signal, confidence, reasons

# ============================================
# CHART FUNCTIONS
# ============================================

def create_candlestick_chart(df, ticker, price_adjuster):
    ticker_name = ticker.replace('.JK', '')
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{ticker_name} - Harga (IDR)", "Volume", "RSI")
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Harga",
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    
    # Moving averages
    if 'ma20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['ma20'], 
                      name="MA20", line=dict(color='orange', width=1.5)),
            row=1, col=1
        )
    
    if 'ma50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['ma50'], 
                      name="MA50", line=dict(color='blue', width=1.5)),
            row=1, col=1
        )
    
    # Bollinger Bands
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_upper'], 
                      name="BB Upper", line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_lower'], 
                      name="BB Lower", line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
    
    # Volume
    colors = ['red' if row['Open'] > row['Close'] else 'green' 
              for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=colors),
        row=2, col=1
    )
    
    # RSI
    if 'rsi' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['rsi'], 
                      name="RSI", line=dict(color='purple', width=2)),
            row=3, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Overbought", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Oversold", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{ticker_name} - Analisis Teknikal (Stockbit Adjusted)",
        template="plotly_dark",
        height=800,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Harga (IDR)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    
    return fig

# ============================================
# MAIN APP (AUTHENTICATED)
# ============================================

def main_app():
    """Main dashboard application (only accessible after login)"""
    
    # Check session timeout (30 minutes)
    if 'last_activity' in st.session_state:
        time_diff = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
        if time_diff > 30:
            logout()
    st.session_state.last_activity = datetime.now()
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1.5, 0.5])
    
    with col1:
        st.title("📊 Saham Indo Dashboard")
        st.caption(f"Bursa Efek Indonesia (IDX) | Trading Hours: {IDX_INFO['trading_hours']} | 1 Lot = {IDX_INFO['lot_size']} Saham")
    
    with col2:
        st.markdown(f"""
        <div class="user-info">
            <strong>👤 {st.session_state.user_info['name']}</strong><br>
            Role: {st.session_state.user_info['role'].upper()}<br>
            Last Login: {st.session_state.user_info.get('last_login', 'First time')[:19]}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Stockbit info note
    st.markdown("""
    <div class="stockbit-note">
        📌 <strong>Stockbit Standard:</strong> Harga telah disesuaikan dengan standar Stockbit | 1 Lot = 100 saham | 
        Nilai per lot = Harga × 100
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize managers
    tm = TickerManager()
    dm = DataManager()
    fe = FeatureEngineer()
    sg = SignalGenerator()
    price_adjuster = StockbitPriceAdjuster()
    
    # Sidebar
    with st.sidebar:
        st.header("📈 Manajemen Portfolio")
        
        # Market info
        with st.expander("ℹ️ Info Pasar", expanded=False):
            st.info(f"**Exchange:** {IDX_INFO['exchange']}")
            st.info(f"**Jam Trading:** {IDX_INFO['trading_hours']}")
            st.info(f"**Mata Uang:** {IDX_INFO['currency']}")
            st.info(f"**1 Lot:** {IDX_INFO['lot_size']} saham")
        
        # Load tickers
        tickers = tm.load()
        
        # Validate tickers
        valid_tickers = []
        invalid_tickers = []
        
        with st.spinner("Validasi saham..."):
            for t in tickers:
                try:
                    test = yf.download(t, period="5d", progress=False)
                    if not test.empty:
                        valid_tickers.append(t)
                    else:
                        invalid_tickers.append(t)
                except:
                    invalid_tickers.append(t)
        
        if invalid_tickers:
            st.warning(f"⚠️ Tidak valid: {', '.join([t.replace('.JK', '') for t in invalid_tickers[:5]])}")
        
        # Role-based access for adding tickers
        user_role = st.session_state.user_info['role']
        
        if user_role == 'admin':
            st.subheader("➕ Tambah Saham")
            new_ticker = st.text_input("Kode Saham", placeholder="BBCA", key="new_ticker")
            if st.button("Tambah", use_container_width=True):
                if new_ticker:
                    ticker_with_suffix = new_ticker.upper()
                    if not ticker_with_suffix.endswith('.JK'):
                        ticker_with_suffix = ticker_with_suffix + '.JK'
                    
                    test = yf.download(ticker_with_suffix, period="5d", progress=False)
                    if not test.empty:
                        if tm.add(new_ticker.upper()):
                            st.success(f"Berhasil menambah {new_ticker.upper()}")
                            st.rerun()
                    else:
                        st.error("Kode saham tidak valid")
        
        # Remove ticker (admin only)
        if valid_tickers and user_role == 'admin':
            st.subheader("🗑️ Hapus Saham")
            remove_ticker = st.selectbox("Pilih", valid_tickers, 
                                        format_func=lambda x: x.replace('.JK', ''), 
                                        key="remove_ticker")
            if st.button("Hapus", use_container_width=True):
                if tm.remove(remove_ticker):
                    st.success(f"Berhasil menghapus {remove_ticker.replace('.JK', '')}")
                    st.rerun()
        
        # Auto sync
        auto_sync = st.toggle("🔄 Auto Sync Data", value=True)
        
        # Change password section
        st.divider()
        with st.expander("🔐 Ganti Password"):
            with st.form("change_password_form"):
                old_pass = st.text_input("Password Lama", type="password")
                new_pass = st.text_input("Password Baru", type="password")
                confirm_pass = st.text_input("Konfirmasi Password Baru", type="password")
                
                if st.form_submit_button("Ganti Password"):
                    if new_pass != confirm_pass:
                        st.error("Password baru tidak cocok!")
                    elif len(new_pass) < 6:
                        st.error("Password minimal 6 karakter!")
                    else:
                        auth = AuthManager()
                        success, message = auth.change_password(
                            st.session_state.username, old_pass, new_pass
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.divider()
        st.info(f"📊 Total saham: {len(valid_tickers)}")
    
    if not valid_tickers:
        st.warning("⚠️ Belum ada saham yang valid. Silakan tambah saham menggunakan sidebar.")
        return
    
    # Main content
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected = st.selectbox(
            "Pilih Saham", 
            valid_tickers,
            format_func=lambda x: x.replace('.JK', '')
        )
    
    with col2:
        period = st.selectbox(
            "Periode", 
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            format_func=lambda x: {
                "1mo": "1 Bulan",
                "3mo": "3 Bulan", 
                "6mo": "6 Bulan",
                "1y": "1 Tahun",
                "2y": "2 Tahun",
                "5y": "5 Tahun"
            }.get(x, x)
        )
    
    with col3:
        chart_type = st.selectbox(
            "Tipe Chart",
            ["Candlestick", "Line", "OHLC"],
            index=0
        )
    
    # Load data
    if auto_sync or selected:
        with st.spinner(f"Memuat data {selected.replace('.JK', '')}..."):
            df = dm.download(selected, period=period)
    
    if df is None or df.empty:
        st.error(f"Gagal memuat data {selected.replace('.JK', '')}")
        return
    
    # Generate features
    with st.spinner("Menghitung indikator teknikal..."):
        feat = fe.transform(df)
    
    if feat.empty:
        st.error("Gagal menghitung indikator")
        return
    
    # Latest data
    latest = feat.iloc[-1]
    
    # Generate signal
    signal, confidence, reasons = sg.generate_signal(latest)
    
    # Display signal
    if signal == "BUY":
        st.markdown("""
            <div class="signal-buy">
                <h2>🟢 SINYAL BELI</h2>
                <p>Teridentifikasi peluang beli yang kuat</p>
            </div>
        """, unsafe_allow_html=True)
    elif signal == "SELL":
        st.markdown("""
            <div class="signal-sell">
                <h2>🔴 SINYAL JUAL</h2>
                <p>Pertimbangkan untuk mengurangi posisi atau mengambil keuntungan</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="signal-hold">
                <h2>🟡 TAHAN</h2>
                <p>Tidak ada sinyal jelas, pertahankan posisi saat ini</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Metrics with Stockbit lot calculation
    st.subheader("📈 Metrik Utama")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price_change = ((latest['Close'] / feat.iloc[-2]['Close'] - 1) * 100) if len(feat) > 1 else 0
        lot_value = price_adjuster.calculate_lot_value(latest['Close'])
        st.metric(
            "Harga per Saham", 
            price_adjuster.format_stockbit_price(latest['Close']), 
            f"{price_change:+.2f}%"
        )
        st.caption(f"1 Lot = {price_adjuster.format_stockbit_price(lot_value)}")
    
    with col2:
        rsi_status = ""
        if latest['rsi'] > 70:
            rsi_status = "Overbought"
        elif latest['rsi'] < 30:
            rsi_status = "Oversold"
        st.metric("RSI (14)", f"{latest['rsi']:.1f}", rsi_status)
    
    with col3:
        trend = "Bullish" if latest['ma20'] > latest['ma50'] else "Bearish"
        st.metric("Trend", trend)
    
    with col4:
        st.metric("MA20", price_adjuster.format_stockbit_price(latest['ma20']))
    
    with col5:
        st.metric("MA50", price_adjuster.format_stockbit_price(latest['ma50']))
    
    # Additional metrics
    st.subheader("📊 Indikator Tambahan")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("MACD", f"{latest['macd']:,.0f}")
    
    with col2:
        st.metric("Volume Ratio", f"{latest['volume_ratio']:.2f}x")
    
    with col3:
        st.metric("Volatilitas", f"{latest['volatility']:.2f}%")
    
    with col4:
        bb_width = latest.get('bb_width', 0)
        st.metric("BB Width", f"{bb_width:.2f}%")
    
    # Support/Resistance with lot value
    col1, col2 = st.columns(2)
    with col1:
        support_lot = price_adjuster.calculate_lot_value(latest.get('support', 0))
        st.metric("Support", price_adjuster.format_stockbit_price(latest.get('support', 0)))
        st.caption(f"1 Lot: {price_adjuster.format_stockbit_price(support_lot)}")
    with col2:
        resistance_lot = price_adjuster.calculate_lot_value(latest.get('resistance', 0))
        st.metric("Resistance", price_adjuster.format_stockbit_price(latest.get('resistance', 0)))
        st.caption(f"1 Lot: {price_adjuster.format_stockbit_price(resistance_lot)}")
    
    # Signal reasons
    if reasons:
        st.subheader("🎯 Faktor Sinyal")
        for reason in reasons:
            st.info(f"✓ {reason}")
    
    # Confidence
    st.subheader("💪 Tingkat Keyakinan")
    st.progress(confidence, text=f"{confidence:.0%}")
    
    # Chart
    st.subheader("📉 Chart Teknikal (Stockbit Adjusted)")
    fig = create_candlestick_chart(feat.tail(100), selected, price_adjuster)
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick stats table
    st.subheader("📊 Statistik Singkat")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recent_returns = feat['ret1'].tail(5).mean() * 100
        st.metric("Rata-rata Return (5 hari)", f"{recent_returns:+.2f}%")
    
    with col2:
        highest = feat['High'].max()
        lowest = feat['Low'].min()
        st.metric("Range Harga", f"{price_adjuster.format_stockbit_price(lowest)} - {price_adjuster.format_stockbit_price(highest)}")
        st.caption(f"Range per Lot: {price_adjuster.format_stockbit_price(lowest * 100)} - {price_adjuster.format_stockbit_price(highest * 100)}")
    
    with col3:
        volume_trend = feat['volume_ratio'].iloc[-1]
        volume_status = "Meningkat" if volume_trend > 1 else "Menurun"
        st.metric("Volume Trend", volume_status, f"{volume_trend:.2f}x")
    
    # Data table
    with st.expander("📋 Lihat Data Historis (Stockbit Adjusted)", expanded=False):
        display_df = feat.tail(30).copy()
        # Format for display with Stockbit prices
        for col in ['Close', 'Open', 'High', 'Low', 'ma20', 'ma50', 'support', 'resistance']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: price_adjuster.format_stockbit_price(x))
        if 'Volume' in display_df.columns:
            display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
        if 'rsi' in display_df.columns:
            display_df['rsi'] = display_df['rsi'].apply(lambda x: f"{x:.1f}")
        if 'volume_ratio' in display_df.columns:
            display_df['volume_ratio'] = display_df['volume_ratio'].apply(lambda x: f"{x:.2f}x")
        
        st.dataframe(display_df, use_container_width=True, height=400)
    
    # Footer
    st.divider()
    st.caption(f"Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB")
    st.caption("Data: Yahoo Finance (disesuaikan dengan standar Stockbit) | Analisis hanya untuk referensi, bukan rekomendasi investasi")
    st.caption("📌 1 Lot = 100 saham | Harga per lot = Harga saham × 100")

# ============================================
# APP ENTRY POINT
# ============================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()