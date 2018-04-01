from collections import OrderedDict
from datetime import datetime
from zipline import TradingAlgorithm
from zipline.api import order, symbol, record
from zipline.data.loader import load_prices_from_csv
import pandas as pd
import pytz


FILE_PATH = 'bitmap.csv'

def initialize(context):
    pass

def handle_data(context, data):
    print(data)

def convert_column_timestamp_to_date():
    file_path = 'bitstampUSD_1-min_data_2012-01-01_to_2018-03-27.csv'
    #file_path = 'AAPL.csv' 
    data = OrderedDict()
    data['BITSTAMPUSD'] = pd.read_csv(file_path)
    # retorna pandas Series com os dados da Coluna Timestamp convertidos para date
    timestamp = data['BITSTAMPUSD']['Timestamp'].apply(lambda x: datetime.fromtimestamp(int(x)).strftime("%d/%m/%Y %H:%M:%S"))
    # atualizando o Dataframe com a coluna Timestamp convertido para date 
    data['BITSTAMPUSD'].update(timestamp)
    #print(data['BITSTAMPUSD'].head())
    #print(data['BITSTAMPUSD'].keys())
    # salvando em arquivo o Dataframe
    data['BITSTAMPUSD'].to_csv('bitmapUSD.csv', index=False)
    #print(timestamp)

def main():
    #file_path = 'AAPL.csv' 
    print("Reading csv file...")
    data = OrderedDict()
    data['BITSTAMPUSD'] = pd.read_csv(FILE_PATH, index_col=0, parse_dates=['Timestamp'])
    #print(data['BITSTAMPUSD'].head())
    print(data['BITSTAMPUSD'].keys())
    # salvando em arquivo o Dataframe

    # convertendo o pandas Dataframe em pandas Panel
    panel = pd.Panel(data)
    panel.minor_axis = ['Open', 'High', 'Low', 'Close', 'Volume_(BTC)', 'Volume_(Currency)', 'Weighted_Price']
    #panel.minor_axis = ['Open', 'High', 'Low', 'Close', 'Volume']
    panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
    #print(panel)
    print("Starting zipline..")
    alg_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    print("Running zipline..")
    perf_manual = alg_obj.run(panel)
    print("Finished")


if __name__ == '__main__':
    main()
    #convert_column_timestamp_to_date()
