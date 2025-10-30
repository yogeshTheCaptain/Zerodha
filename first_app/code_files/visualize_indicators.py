"""
Script to visualize technical indicators
Install required: pip install matplotlib
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from code_files.indicators import ZerodhaIndicators
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def plot_price_with_sma(csv_file, num_candles=100):
    """
    Plot price with moving averages
    
    Args:
        csv_file (str): CSV file path
        num_candles (int): Number of recent candles to plot
    """
    # Load and add indicators
    ind = ZerodhaIndicators(csv_file=csv_file)
    ind.add_sma(20)
    ind.add_sma(50)
    ind.add_ema(20)
    
    df = ind.get_dataframe().tail(num_candles).copy()
    
    # Create datetime column for x-axis - handle different time formats
    try:
        # Try direct conversion first
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].astype(str))
    except:
        # If that fails, try converting Time column differently
        df['Time_str'] = df['Time'].apply(lambda x: str(x) if pd.notna(x) else '00:00:00')
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time_str'])
    
    # Debug: Print first few datetime values
    print(f"Sample DateTime values:\n{df[['Date', 'Time', 'DateTime']].head()}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # Plot price and moving averages
    ax.plot(df['DateTime'], df['close'], label='Close', linewidth=2, color='black')
    ax.plot(df['DateTime'], df['SMA_20'], label='SMA 20', linewidth=1.5, color='blue', alpha=0.7)
    ax.plot(df['DateTime'], df['SMA_50'], label='SMA 50', linewidth=1.5, color='red', alpha=0.7)
    ax.plot(df['DateTime'], df['EMA_20'], label='EMA 20', linewidth=1.5, color='green', alpha=0.7, linestyle='--')
    
    # Format x-axis to show dates and times properly
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b\n%H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=0, ha='center')
    
    ax.set_title('Price with Moving Averages', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date & Time', fontsize=12)
    ax.set_ylabel('Price', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('price_with_sma.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: price_with_sma.png")
    plt.show()


def plot_rsi(csv_file, num_candles=100):
    """
    Plot RSI indicator
    
    Args:
        csv_file (str): CSV file path
        num_candles (int): Number of recent candles to plot
    """
    # Load and add RSI
    ind = ZerodhaIndicators(csv_file=csv_file)
    ind.add_rsi(14)
    
    df = ind.get_dataframe().tail(num_candles)
    
    # Create datetime column
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].astype(str))
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[2, 1])
    
    # Plot price
    ax1.plot(df['DateTime'], df['close'], label='Close', linewidth=2, color='black')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.set_title('Price Chart', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot RSI
    ax2.plot(df['DateTime'], df['RSI_14'], label='RSI 14', linewidth=2, color='purple')
    ax2.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
    ax2.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
    ax2.fill_between(df['DateTime'], 30, 70, alpha=0.1, color='gray')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax2.set_title('RSI Indicator', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date & Time', fontsize=12)
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rsi_chart.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: rsi_chart.png")
    plt.show()


def plot_macd(csv_file, num_candles=100):
    """
    Plot MACD indicator
    
    Args:
        csv_file (str): CSV file path
        num_candles (int): Number of recent candles to plot
    """
    # Load and add MACD
    ind = ZerodhaIndicators(csv_file=csv_file)
    ind.add_macd()
    
    df = ind.get_dataframe().tail(num_candles)
    
    # Create datetime column
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].astype(str))
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[2, 1])
    
    # Plot price
    ax1.plot(df['DateTime'], df['close'], label='Close', linewidth=2, color='black')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.set_title('Price Chart', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot MACD
    ax2.plot(df['DateTime'], df['MACD'], label='MACD', linewidth=2, color='blue')
    ax2.plot(df['DateTime'], df['MACD_Signal'], label='Signal', linewidth=2, color='red')
    ax2.bar(df['DateTime'], df['MACD_Histogram'], label='Histogram', alpha=0.3, color='gray')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax2.set_title('MACD Indicator', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date & Time', fontsize=12)
    ax2.set_ylabel('MACD', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('macd_chart.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: macd_chart.png")
    plt.show()


def plot_bollinger_bands(csv_file, num_candles=100):
    """
    Plot Bollinger Bands
    
    Args:
        csv_file (str): CSV file path
        num_candles (int): Number of recent candles to plot
    """
    # Load and add Bollinger Bands
    ind = ZerodhaIndicators(csv_file=csv_file)
    ind.add_bollinger_bands()
    
    df = ind.get_dataframe().tail(num_candles)
    
    # Create datetime column
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].astype(str))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # Plot Bollinger Bands
    ax.plot(df['DateTime'], df['close'], label='Close', linewidth=2, color='black')
    ax.plot(df['DateTime'], df['BB_Upper'], label='Upper Band', linewidth=1.5, color='red', linestyle='--')
    ax.plot(df['DateTime'], df['BB_Middle'], label='Middle Band (SMA)', linewidth=1.5, color='blue')
    ax.plot(df['DateTime'], df['BB_Lower'], label='Lower Band', linewidth=1.5, color='green', linestyle='--')
    ax.fill_between(df['DateTime'], df['BB_Upper'], df['BB_Lower'], alpha=0.1, color='gray')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.xticks(rotation=45, ha='right')
    
    ax.set_title('Bollinger Bands', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date & Time', fontsize=12)
    ax.set_ylabel('Price', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bollinger_bands.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: bollinger_bands.png")
    plt.show()


def plot_complete_analysis(csv_file, num_candles=100):
    """
    Complete technical analysis with multiple indicators
    
    Args:
        csv_file (str): CSV file path
        num_candles (int): Number of recent candles to plot
    """
    # Load and add all indicators
    ind = ZerodhaIndicators(csv_file=csv_file)
    ind.add_sma(20)
    ind.add_sma(50)
    ind.add_rsi(14)
    ind.add_macd()
    ind.add_bollinger_bands()
    ind.add_volume_sma(20)
    
    df = ind.get_dataframe().tail(num_candles)
    
    # Create datetime column
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].astype(str))
    
    # Create figure with 4 subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.3)
    
    ax1 = fig.add_subplot(gs[0])  # Price with Bollinger Bands
    ax2 = fig.add_subplot(gs[1])  # Volume
    ax3 = fig.add_subplot(gs[2])  # RSI
    ax4 = fig.add_subplot(gs[3])  # MACD
    
    # 1. Price with Bollinger Bands and Moving Averages
    ax1.plot(df['DateTime'], df['close'], label='Close', linewidth=2, color='black', zorder=5)
    ax1.plot(df['DateTime'], df['BB_Upper'], label='BB Upper', linewidth=1, color='red', linestyle='--', alpha=0.5)
    ax1.plot(df['DateTime'], df['BB_Middle'], label='BB Middle', linewidth=1, color='blue', alpha=0.5)
    ax1.plot(df['DateTime'], df['BB_Lower'], label='BB Lower', linewidth=1, color='green', linestyle='--', alpha=0.5)
    ax1.fill_between(df['DateTime'], df['BB_Upper'], df['BB_Lower'], alpha=0.1, color='gray')
    ax1.plot(df['DateTime'], df['SMA_20'], label='SMA 20', linewidth=1.5, color='orange', alpha=0.7)
    ax1.plot(df['DateTime'], df['SMA_50'], label='SMA 50', linewidth=1.5, color='purple', alpha=0.7)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.set_title('Complete Technical Analysis', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Price', fontsize=12)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. Volume
    colors = ['green' if df['close'].iloc[i] >= df['open'].iloc[i] else 'red' 
              for i in range(len(df))]
    ax2.bar(df['DateTime'], df['volume'], color=colors, alpha=0.5, width=0.0003)
    ax2.plot(df['DateTime'], df['Volume_SMA_20'], label='Volume SMA 20', linewidth=1.5, color='blue')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 3. RSI
    ax3.plot(df['DateTime'], df['RSI_14'], label='RSI 14', linewidth=2, color='purple')
    ax3.axhline(y=70, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax3.axhline(y=30, color='g', linestyle='--', linewidth=1, alpha=0.5)
    ax3.fill_between(df['DateTime'], 30, 70, alpha=0.1, color='gray')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax3.set_ylabel('RSI', fontsize=12)
    ax3.set_ylim(0, 100)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 4. MACD
    ax4.plot(df['DateTime'], df['MACD'], label='MACD', linewidth=2, color='blue')
    ax4.plot(df['DateTime'], df['MACD_Signal'], label='Signal', linewidth=2, color='red')
    colors_macd = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
    ax4.bar(df['DateTime'], df['MACD_Histogram'], alpha=0.3, color=colors_macd, width=0.0003)
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax4.set_xlabel('Date & Time', fontsize=12)
    ax4.set_ylabel('MACD', fontsize=12)
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('complete_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: complete_analysis.png")
    plt.show()


def main():
    """Main function to generate all charts"""
    csv_file = 'nifty-50-5min-data.csv'
    num_candles = 200  # Plot last 200 candles
    
    print("="*60)
    print("GENERATING TECHNICAL ANALYSIS CHARTS")
    print("="*60)
    
    try:
        print("\n📊 Generating charts...")
        
        # Generate individual charts
        print("\n1. Price with Moving Averages...")
        plot_price_with_sma(csv_file, num_candles)
        
        print("\n2. RSI Chart...")
        plot_rsi(csv_file, num_candles)
        
        print("\n3. MACD Chart...")
        plot_macd(csv_file, num_candles)
        
        print("\n4. Bollinger Bands...")
        plot_bollinger_bands(csv_file, num_candles)
        
        print("\n5. Complete Analysis...")
        plot_complete_analysis(csv_file, num_candles)
        
        print("\n" + "="*60)
        print("✅ ALL CHARTS GENERATED SUCCESSFULLY!")
        print("="*60)
        
    except FileNotFoundError:
        print(f"\n❌ File not found: {csv_file}")
        print("Please make sure you have historical data downloaded.")
        print("Run: python code_files/download_historical_data.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# if __name__ == "__main__":
#     main()