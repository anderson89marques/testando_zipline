from collections import OrderedDict
from datetime import datetime, date
from zipline import TradingAlgorithm, run_algorithm
from zipline.api import order, symbol, record, set_benchmark
from zipline.finance import commission, slippage
from zipline.data.loader import load_prices_from_csv
import pandas as pd
import pytz

from talib import EMA


#FILE_PATH = 'daily/BITMAP.csv'
FILE_PATH = 'BITMAP.csv'

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


def initialize(context):
    context.asset = symbol('BITMAP')
    context.invested = False
    context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
    context.set_slippage(slippage.VolumeShareSlippage())

def handle_data(context, data):
    #print(data.current(context.asset, ['open', 'high', 'low', 'close', 'price']))
    #print(context)
    trailing_window = data.history(context.asset, 'price', 40, '1m')
    if trailing_window.isnull().values.any():
        return
    short_ema = EMA(trailing_window.values, timeperiod=20)
    long_ema = EMA(trailing_window.values, timeperiod=40)
    #print(short_ema)
    #print(long_ema)
    buy = False
    sell = False

    if (short_ema[-1] > long_ema[-1]) and not context.invested:
        order(context.asset, 1000)
        context.invested = True
        buy = True
    elif (short_ema[-1] < long_ema[-1]) and context.invested:
        order(context.asset, -1000)
        context.invested = False
        sell = True

    record(BITMAP=data.current(context.asset, "price"),
           short_ema=short_ema[-1],
           long_ema=long_ema[-1],
           buy=buy,
           sell=sell)

def analyze(context=None, results=None):
    import matplotlib.pyplot as plt
    import logbook
    logbook.StderrHandler().push_application()
    log = logbook.Logger('Algorithm')

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('Portfolio value (USD)')

    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('Price (USD)')

    # If data has been record()ed, then plot it.
    # Otherwise, log the fact that no data has been recorded.
    if 'BITMAP' in results and 'short_ema' in results and 'long_ema' in results:
        results[['BITMAP', 'short_ema', 'long_ema']].plot(ax=ax2)

        ax2.plot(
            results.index[results.buy],
            results.loc[results.buy, 'long_ema'],
            '^',
            markersize=10,
            color='m',
        )
        ax2.plot(
            results.index[results.sell],
            results.loc[results.sell, 'short_ema'],
            'v',
            markersize=10,
            color='k',
        )
        plt.legend(loc=0)
        plt.gcf().set_size_inches(18, 8)
    else:
        msg = 'BITMAP, short_ema and long_ema data not captured using record().'
        ax2.annotate(msg, xy=(0.1, 0.5))
        log.info(msg)

    plt.show()


def main():
    #file_path = 'AAPL.csv' 
    print("Reading csv file...")
    data = OrderedDict()
    data['BITMAP'] = pd.read_csv(FILE_PATH, index_col=0, parse_dates=['timestamp'])
    print(data['BITMAP'].head())
    print(data['BITMAP'].keys())
    # salvando em arquivo o Dataframe

    # convertendo o pandas Dataframe em pandas Panel
    panel = pd.Panel(data)
    panel.minor_axis = ['open', 'high', 'low', 'close', 'volume', 'volume_(currency)', 'weighted_price']
    #panel.minor_axis = ['Open', 'High', 'Low', 'Close', 'Volume']
    panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
    print(panel)
    print("Starting zipline..")
    #alg_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    capital_base = 50000
    start = datetime(2016, 1, 1, 0,0,0,0, pytz.utc)
    end = datetime(2016, 2, 1, 0,0,0,0, pytz.utc)
    print("Running zipline..")
    run_algorithm(start=start, end=end, initialize=initialize, capital_base=capital_base,
                  handle_data=handle_data, analyze=analyze, data=panel, data_frequency='minute')
    #perf_manual = alg_obj.run(panel)
    print("Finished")


if __name__ == '__main__':
    main()
    #convert_column_timestamp_to_date()
