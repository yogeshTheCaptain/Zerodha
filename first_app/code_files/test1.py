import os
from first_app.code_files.historical_data_download import ZerodhaHistoricalData
from first_app.code_files.indicators import ZerodhaIndicators
from first_app.constants import *
from first_app.code_files.visualize_indicators import plot_rsi

hist_data_obj = ZerodhaHistoricalData()

ticker = "RPOWER"
# ticker = "HINDZINC"
inception_date = "01-01-2025"
interval = "5minute"

output_file = f"{historical_data_folder}/{ticker}.csv"
indicator_file_name = f"{historical_data_folder}/{ticker}_with_indicators.csv"

os.makedirs(historical_data_folder, exist_ok=True)


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

