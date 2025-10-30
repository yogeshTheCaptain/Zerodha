import os
from first_app.code_files.historical_data_download import ZerodhaHistoricalData
from first_app.code_files.indicators import ZerodhaIndicators
from first_app.code_files.visualize_indicators import plot_rsi

hist_data_obj = ZerodhaHistoricalData(token_file='zerodha_tokens.json')

ticker = "RPOWER"
# ticker = "HINDZINC"
inception_date = "01-01-2025"
interval = "5minute"
output_folder  = "historical_data"
output_file = f"{output_folder}/{ticker}.csv"

os.makedirs(output_folder, exist_ok=True)

indicator_file_name = f"{output_folder}/{ticker}_with_indicators.csv"

ohlc = hist_data_obj.fetch_ohlc(
    ticker = ticker,
    inception_date = inception_date,
    interval = interval,
    output_file = output_file
)

indicators = ZerodhaIndicators(csv_file = output_file)
indicators.add_rsi(14)
indicators.save_to_csv(indicator_file_name)

indicators.get_indicator_summary()

# plot_rsi(output_file, 5000)

