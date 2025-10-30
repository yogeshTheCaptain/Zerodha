import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from pathlib import Path


class ZerodhaIndicators:
    """
    Class to apply technical indicators on historical data
    """
    
    def __init__(self, csv_file=None, dataframe=None):
        """
        Initialize with either a CSV file or a DataFrame
        
        Args:
            csv_file (str): Path to CSV file with historical data
            dataframe (pd.DataFrame): DataFrame with historical data
        """
        if csv_file:
            self.df = pd.read_csv(csv_file)
            print(f"✅ Loaded data from {csv_file}")
        elif dataframe is not None:
            self.df = dataframe.copy()
            print(f"✅ Loaded data from DataFrame")
        else:
            raise ValueError("Either csv_file or dataframe must be provided")
        
        print(f"   Total records: {len(self.df)}")
        self._validate_data()
    
    def _validate_data(self):
        """Validate that required columns exist"""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        print(f"   Columns: {list(self.df.columns)}")
    
    # ==========================================
    # Moving Averages
    # ==========================================
    
    def add_sma(self, period=20, column='close', name=None):
        """
        Add Simple Moving Average
        
        Args:
            period (int): Period for SMA
            column (str): Column to calculate SMA on
            name (str): Custom column name (optional)
        """
        col_name = name or f'SMA_{period}'
        self.df[col_name] = self.df[column].rolling(window=period).mean()
        print(f"✅ Added {col_name}")
        return self
    
    def add_ema(self, period=20, column='close', name=None):
        """
        Add Exponential Moving Average
        
        Args:
            period (int): Period for EMA
            column (str): Column to calculate EMA on
            name (str): Custom column name (optional)
        """
        col_name = name or f'EMA_{period}'
        self.df[col_name] = self.df[column].ewm(span=period, adjust=False).mean()
        print(f"✅ Added {col_name}")
        return self
    
    def add_wma(self, period=20, column='close', name=None):
        """
        Add Weighted Moving Average
        
        Args:
            period (int): Period for WMA
            column (str): Column to calculate WMA on
            name (str): Custom column name (optional)
        """
        col_name = name or f'WMA_{period}'
        weights = np.arange(1, period + 1)
        self.df[col_name] = self.df[column].rolling(window=period).apply(
            lambda prices: np.dot(prices, weights) / weights.sum(), raw=True
        )
        print(f"✅ Added {col_name}")
        return self
    
    # ==========================================
    # RSI (Relative Strength Index)
    # ==========================================
    
    def add_rsi(self, period=14, column='close', name=None):
        """
        Add Relative Strength Index
        
        Args:
            period (int): Period for RSI
            column (str): Column to calculate RSI on
            name (str): Custom column name (optional)
        """
        col_name = name or f'RSI_{period}'
        
        delta = self.df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        self.df[col_name] = 100 - (100 / (1 + rs))
        print(f"✅ Added {col_name}")
        return self
    
    # ==========================================
    # MACD (Moving Average Convergence Divergence)
    # ==========================================
    
    def add_macd(self, fast=12, slow=26, signal=9, column='close'):
        """
        Add MACD indicator
        
        Args:
            fast (int): Fast EMA period
            slow (int): Slow EMA period
            signal (int): Signal line period
            column (str): Column to calculate MACD on
        """
        exp1 = self.df[column].ewm(span=fast, adjust=False).mean()
        exp2 = self.df[column].ewm(span=slow, adjust=False).mean()
        
        self.df['MACD'] = exp1 - exp2
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=signal, adjust=False).mean()
        self.df['MACD_Histogram'] = self.df['MACD'] - self.df['MACD_Signal']
        
        print(f"✅ Added MACD (Fast={fast}, Slow={slow}, Signal={signal})")
        return self
    
    # ==========================================
    # Bollinger Bands
    # ==========================================
    
    def add_bollinger_bands(self, period=20, std_dev=2, column='close'):
        """
        Add Bollinger Bands
        
        Args:
            period (int): Period for moving average
            std_dev (int): Number of standard deviations
            column (str): Column to calculate bands on
        """
        self.df['BB_Middle'] = self.df[column].rolling(window=period).mean()
        rolling_std = self.df[column].rolling(window=period).std()
        
        self.df['BB_Upper'] = self.df['BB_Middle'] + (rolling_std * std_dev)
        self.df['BB_Lower'] = self.df['BB_Middle'] - (rolling_std * std_dev)
        self.df['BB_Width'] = self.df['BB_Upper'] - self.df['BB_Lower']
        
        print(f"✅ Added Bollinger Bands (Period={period}, StdDev={std_dev})")
        return self
    
    # ==========================================
    # ATR (Average True Range)
    # ==========================================
    
    def add_atr(self, period=14, name=None):
        """
        Add Average True Range
        
        Args:
            period (int): Period for ATR
            name (str): Custom column name (optional)
        """
        col_name = name or f'ATR_{period}'
        
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.df[col_name] = true_range.rolling(window=period).mean()
        
        print(f"✅ Added {col_name}")
        return self
    
    # ==========================================
    # Stochastic Oscillator
    # ==========================================
    
    def add_stochastic(self, k_period=14, d_period=3):
        """
        Add Stochastic Oscillator
        
        Args:
            k_period (int): Period for %K
            d_period (int): Period for %D
        """
        lowest_low = self.df['low'].rolling(window=k_period).min()
        highest_high = self.df['high'].rolling(window=k_period).max()
        
        self.df['Stoch_K'] = 100 * ((self.df['close'] - lowest_low) / (highest_high - lowest_low))
        self.df['Stoch_D'] = self.df['Stoch_K'].rolling(window=d_period).mean()
        
        print(f"✅ Added Stochastic (K={k_period}, D={d_period})")
        return self
    
    # ==========================================
    # ADX (Average Directional Index)
    # ==========================================
    
    def add_adx(self, period=14):
        """
        Add Average Directional Index
        
        Args:
            period (int): Period for ADX
        """
        high_diff = self.df['high'].diff()
        low_diff = -self.df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculate ATR
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        self.df['ADX'] = dx.rolling(window=period).mean()
        self.df['Plus_DI'] = plus_di
        self.df['Minus_DI'] = minus_di
        
        print(f"✅ Added ADX (Period={period})")
        return self
    
    # ==========================================
    # Volume Indicators
    # ==========================================
    
    def add_volume_sma(self, period=20):
        """Add Simple Moving Average of Volume"""
        self.df[f'Volume_SMA_{period}'] = self.df['volume'].rolling(window=period).mean()
        print(f"✅ Added Volume_SMA_{period}")
        return self
    
    def add_obv(self):
        """Add On-Balance Volume"""
        obv = [0]
        for i in range(1, len(self.df)):
            if self.df['close'].iloc[i] > self.df['close'].iloc[i-1]:
                obv.append(obv[-1] + self.df['volume'].iloc[i])
            elif self.df['close'].iloc[i] < self.df['close'].iloc[i-1]:
                obv.append(obv[-1] - self.df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        self.df['OBV'] = obv
        print(f"✅ Added OBV (On-Balance Volume)")
        return self
    
    # ==========================================
    # Pivot Points
    # ==========================================
    
    def add_pivot_points(self):
        """Add Classic Pivot Points"""
        self.df['Pivot'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        self.df['R1'] = 2 * self.df['Pivot'] - self.df['low']
        self.df['S1'] = 2 * self.df['Pivot'] - self.df['high']
        self.df['R2'] = self.df['Pivot'] + (self.df['high'] - self.df['low'])
        self.df['S2'] = self.df['Pivot'] - (self.df['high'] - self.df['low'])
        
        print(f"✅ Added Pivot Points")
        return self
    
    # ==========================================
    # Candlestick Patterns (Basic)
    # ==========================================
    
    def add_candlestick_patterns(self):
        """Identify basic candlestick patterns"""
        # Doji
        body = abs(self.df['close'] - self.df['open'])
        range_val = self.df['high'] - self.df['low']
        self.df['Doji'] = (body / range_val < 0.1).astype(int)
        
        # Hammer
        lower_shadow = self.df[['open', 'close']].min(axis=1) - self.df['low']
        upper_shadow = self.df['high'] - self.df[['open', 'close']].max(axis=1)
        self.df['Hammer'] = ((lower_shadow > 2 * body) & (upper_shadow < body)).astype(int)
        
        # Bullish Engulfing (simplified)
        prev_close = self.df['close'].shift(1)
        prev_open = self.df['open'].shift(1)
        self.df['Bullish_Engulfing'] = (
            (self.df['close'] > self.df['open']) &
            (prev_close < prev_open) &
            (self.df['open'] < prev_close) &
            (self.df['close'] > prev_open)
        ).astype(int)
        
        print(f"✅ Added Candlestick Patterns (Doji, Hammer, Bullish Engulfing)")
        return self
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
    def add_all_basic_indicators(self):
        """Add all basic commonly used indicators"""
        print("\n📊 Adding all basic indicators...")
        self.add_sma(20)
        self.add_ema(20)
        self.add_sma(50)
        self.add_sma(200)
        self.add_rsi(14)
        self.add_macd()
        self.add_bollinger_bands()
        self.add_atr()
        self.add_volume_sma(20)
        print("✅ All basic indicators added!")
        return self
    
    def get_dataframe(self):
        """Return the DataFrame with indicators"""
        return self.df
    
    def save_to_csv(self, output_file):
        """
        Save DataFrame with indicators to CSV
        
        Args:
            output_file (str): Output file path
        """
        self.df.to_csv(output_file, index=False)
        print(f"✅ Data with indicators saved to {output_file}")
    
    def get_latest_values(self, num_rows=5):
        """
        Get latest values with indicators
        
        Args:
            num_rows (int): Number of latest rows to return
        """
        return self.df.tail(num_rows)
    
    def get_indicator_summary(self):
        """Get summary of all indicators in the dataset"""
        print("\n" + "="*60)
        print("INDICATOR SUMMARY")
        print("="*60)
        
        indicator_cols = [col for col in self.df.columns 
                         if col not in ['Date', 'Time', 'open', 'high', 'low', 'close', 'volume']]
        
        print(f"Total indicators: {len(indicator_cols)}")
        print("\nIndicators present:")
        for col in indicator_cols:
            non_null = self.df[col].notna().sum()
            print(f"  • {col}: {non_null} valid values")


# # Example usage
# if __name__ == "__main__":
#     print("="*60)
#     print("Zerodha Technical Indicators Example")
#     print("="*60)
    
#     # Load data from CSV
#     indicators = ZerodhaIndicators(csv_file='nifty-50-5min-data.csv')
    
#     # Add individual indicators
#     indicators.add_sma(20)
#     indicators.add_ema(50)
#     indicators.add_rsi(14)
#     indicators.add_macd()
#     indicators.add_bollinger_bands()
    
#     # Or add all basic indicators at once
#     # indicators.add_all_basic_indicators()
    
#     # Save with indicators
#     indicators.save_to_csv('nifty-50-with-indicators.csv')
    
#     # Get latest values
#     print("\nLatest 5 rows with indicators:")
#     print(indicators.get_latest_values(5))
    
#     # Get summary
#     indicators.get_indicator_summary()