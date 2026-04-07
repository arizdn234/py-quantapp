# utils/chart_utils.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class ChartUtils:
    @staticmethod
    def create_candlestick_chart(df, title="Price Chart"):
        """Create interactive candlestick chart"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(title, "Volume", "RSI")
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"
            ),
            row=1, col=1
        )
        
        # Add moving averages
        if 'ma20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ma20'], 
                          name="MA20", line=dict(color='orange', width=1)),
                row=1, col=1
            )
        
        if 'ma50' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ma50'], 
                          name="MA50", line=dict(color='blue', width=1)),
                row=1, col=1
            )
        
        # Volume bars
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
            
            # Add RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=800,
            hovermode='x unified'
        )
        
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig
    
    @staticmethod
    def create_indicator_chart(df, indicators=['rsi', 'macd', 'volume_ratio']):
        """Create separate indicator charts"""
        fig = make_subplots(
            rows=len(indicators), cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[f"{i.upper()}" for i in indicators]
        )
        
        for idx, indicator in enumerate(indicators, 1):
            if indicator in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[indicator], 
                              name=indicator.upper(), 
                              line=dict(width=2)),
                    row=idx, col=1
                )
                
                # Add zero line for MACD
                if indicator == 'macd':
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=idx, col=1)
        
        fig.update_layout(
            title="Technical Indicators",
            height=400 * len(indicators),
            template="plotly_dark",
            showlegend=False
        )
        
        return fig