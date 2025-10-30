import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from kiteconnect import KiteConnect
from zerodha_config import api_key, api_secret
import datetime as dt
import pandas as pd
import json


class ZerodhaHistoricalData:
    """
    Class to download historical data from Zerodha Kite API
    """
    
    def __init__(self, token_file='zerodha_tokens.json'):
        """
        Initialize ZerodhaHistoricalData
        
        Args:
            token_file (str): Path to the token file
        """
        self.token_file = token_file
        self.kite = None
        self.instrument_df = None
        self._initialize_kite()
        self._load_instruments()
    
    def _initialize_kite(self):
        """Initialize KiteConnect with access token"""
        try:
            # Load tokens from file
            with open(self.token_file, 'r') as f:
                tokens = json.load(f)
            
            access_token = tokens['access_token']
            api_key_from_file = tokens.get('api_key', api_key)
            
            # Initialize KiteConnect
            self.kite = KiteConnect(api_key=api_key_from_file)
            self.kite.set_access_token(access_token)
            
            print(f"✅ KiteConnect initialized with access token")
            
        except FileNotFoundError:
            print(f"❌ Token file '{self.token_file}' not found!")
            print("Please run ZerodhaAutoLogin first to generate tokens.")
            raise
        except Exception as e:
            print(f"❌ Error initializing KiteConnect: {e}")
            raise
    
    def _load_instruments(self, exchange="NSE"):
        """
        Load instrument dump from Zerodha
        
        Args:
            exchange (str): Exchange name (NSE, BSE, NFO, etc.)
        """
        try:
            print(f"Loading {exchange} instruments...")
            instrument_dump = self.kite.instruments(exchange)
            self.instrument_df = pd.DataFrame(instrument_dump)
            print(f"✅ Loaded {len(self.instrument_df)} instruments from {exchange}")
        except Exception as e:
            print(f"❌ Error loading instruments: {e}")
            raise
    
    def save_instruments_to_csv(self, filename=None, exchange="NSE"):
        """
        Save instrument dump to CSV file
        
        Args:
            filename (str): Output filename (optional)
            exchange (str): Exchange name
        """
        if filename is None:
            filename = f"{exchange}_Instruments_{dt.date.today().strftime('%d%m%Y')}.csv"
        
        self.instrument_df.to_csv(filename, index=False)
        print(f"✅ Instruments saved to {filename}")
    
    def instrument_lookup(self, symbol):
        """
        Look up instrument token for a given symbol
        
        Args:
            symbol (str): Trading symbol (e.g., 'NIFTY 50', 'RELIANCE')
            
        Returns:
            int: Instrument token or -1 if not found
        """
        try:
            token = self.instrument_df[
                self.instrument_df.tradingsymbol == symbol
            ].instrument_token.values[0]
            return token
        except:
            print(f"❌ Symbol '{symbol}' not found in instrument list")
            return -1
    
    def fetch_ohlc(self, ticker, inception_date, interval, output_file=None):
        """
        Fetch historical OHLC data for a given ticker
        
        Args:
            ticker (str): Trading symbol (e.g., 'NIFTY 50', 'RELIANCE')
            inception_date (str): Start date in 'dd-mm-yyyy' format
            interval (str): Interval - 'minute', '3minute', '5minute', '10minute', 
                           '15minute', '30minute', '60minute', 'day'
            output_file (str): Optional output CSV filename
            
        Returns:
            pd.DataFrame: OHLC data
        """
        print(f"\n{'='*60}")
        print(f"Fetching data for: {ticker}")
        print(f"From: {inception_date} | Interval: {interval}")
        print(f"{'='*60}\n")
        
        # Get instrument token
        instrument = self.instrument_lookup(ticker)
        if instrument == -1:
            return None
        
        # Parse dates
        from_date = dt.datetime.strptime(inception_date, '%d-%m-%Y')
        to_date = dt.date.today()
        
        # Initialize empty dataframe
        data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        
        # Fetch data in chunks of 100 days
        print("Downloading data...")
        chunk_count = 0
        while True:
            if from_date.date() >= (dt.date.today() - dt.timedelta(100)):
                # Last chunk
                chunk_data = self.kite.historical_data(
                    instrument, 
                    from_date, 
                    dt.date.today(), 
                    interval
                )
                data = pd.concat([data, pd.DataFrame(chunk_data)], ignore_index=True)
                chunk_count += 1
                print(f"  Chunk {chunk_count}: {from_date.date()} to {dt.date.today()}")
                break
            else:
                # Fetch 100-day chunk
                to_date = from_date + dt.timedelta(100)
                chunk_data = self.kite.historical_data(
                    instrument, 
                    from_date, 
                    to_date, 
                    interval
                )
                data = pd.concat([data, pd.DataFrame(chunk_data)], ignore_index=True)
                chunk_count += 1
                print(f"  Chunk {chunk_count}: {from_date.date()} to {to_date.date()}")
                from_date = to_date
        
        print(f"\n✅ Downloaded {len(data)} records")
        
        # Process the data
        data = self._process_data(data)
        
        # Save to CSV if filename provided
        if output_file:
            data.to_csv(output_file, index=False)
            print(f"✅ Data saved to {output_file}")
        
        return data
    
    def _process_data(self, data):
        """
        Process raw data - add Date and Time columns, format properly
        
        Args:
            data (pd.DataFrame): Raw OHLC data
            
        Returns:
            pd.DataFrame: Processed data
        """
        # Set date as index temporarily
        data.set_index("date", inplace=True)
        
        # Reset index to bring date back as column
        data = data.reset_index()
        
        # Convert to datetime
        data['Datetime'] = pd.to_datetime(data['date'])
        
        # Create Date and Time columns
        data['Date'] = data['Datetime'].dt.strftime('%d-%m-%Y')
        data['Time'] = data['Datetime'].dt.time
        
        # Remove timezone information
        data['Datetime'] = data['Datetime'].dt.tz_localize(None)
        
        # Drop intermediate columns
        data = data.drop(columns=['Datetime', 'date'])
        
        # Reorder columns: Date, Time, open, high, low, close, volume
        data = data[['Date', 'Time'] + [col for col in data.columns if col not in ['Date', 'Time']]]
        
        return data
    
    def fetch_multiple_tickers(self, tickers_config, base_output_dir='data'):
        """
        Fetch data for multiple tickers
        
        Args:
            tickers_config (list): List of dicts with keys: ticker, inception_date, interval
            base_output_dir (str): Base directory to save CSV files
            
        Example:
            tickers_config = [
                {'ticker': 'NIFTY 50', 'inception_date': '01-01-2025', 'interval': '5minute'},
                {'ticker': 'RELIANCE', 'inception_date': '01-01-2024', 'interval': 'day'}
            ]
        """
        # Create output directory if it doesn't exist
        output_path = Path(base_output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        for config in tickers_config:
            ticker = config['ticker']
            inception_date = config['inception_date']
            interval = config['interval']
            
            # Generate filename
            ticker_clean = ticker.replace(' ', '-').lower()
            output_file = output_path / f"{ticker_clean}-{interval}-data.csv"
            
            # Fetch data
            try:
                data = self.fetch_ohlc(ticker, inception_date, interval, str(output_file))
                results[ticker] = {'success': True, 'file': str(output_file), 'records': len(data)}
            except Exception as e:
                print(f"❌ Error fetching {ticker}: {e}")
                results[ticker] = {'success': False, 'error': str(e)}
        
        return results
    
    def get_profile(self):
        """Get user profile information"""
        try:
            profile = self.kite.profile()
            return profile
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None


# # Example usage
# if __name__ == "__main__":
#     # Initialize historical data downloader
#     hist_data = ZerodhaHistoricalData(token_file='zerodha_tokens.json')
    
#     # Example 1: Download single ticker
#     print("\n" + "="*60)
#     print("EXAMPLE 1: Single Ticker Download")
#     print("="*60)
    
#     ohlc = hist_data.fetch_ohlc(
#         ticker="NIFTY 50",
#         inception_date="01-01-2025",
#         interval="5minute",
#         output_file="nifty-50-5min-data.csv"
#     )
    
#     if ohlc is not None:
#         print("\nFirst 5 rows:")
#         print(ohlc.head())
#         print("\nLast 5 rows:")
#         print(ohlc.tail())
    
#     # Example 2: Download multiple tickers
#     print("\n" + "="*60)
#     print("EXAMPLE 2: Multiple Tickers Download")
#     print("="*60)
    
#     tickers_config = [
#         {'ticker': 'NIFTY 50', 'inception_date': '01-01-2025', 'interval': '5minute'},
#         {'ticker': 'RELIANCE', 'inception_date': '01-01-2024', 'interval': 'day'},
#         {'ticker': 'TCS', 'inception_date': '01-06-2024', 'interval': '15minute'},
#     ]
    
#     results = hist_data.fetch_multiple_tickers(tickers_config, base_output_dir='historical_data')
    
#     print("\n" + "="*60)
#     print("DOWNLOAD SUMMARY")
#     print("="*60)
#     for ticker, result in results.items():
#         if result['success']:
#             print(f"✅ {ticker}: {result['records']} records -> {result['file']}")
#         else:
#             print(f"❌ {ticker}: {result['error']}")