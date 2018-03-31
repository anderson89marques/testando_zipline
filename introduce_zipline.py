import pytz
from datetime import datetime

from zipline.api import order, record, symbol, order_target
from zipline import TradingAlgorithm
from zipline.data.loader import load_from_yahoo


#from pandas_datareader.google.daily import GoogleDailyReader
#import pandas_datareader as pdr

#@property
#def url(self):
#    return 'http://finance.google.com/finance/historical'

#GoogleDailyReader.url = url


START = datetime(2011, 5, 27, 0, 0, 0, 0, pytz.utc).date()
END = datetime(2012,1,1,0,0,0,0, pytz.utc).date()
DATA = load_from_yahoo(stocks=['AAPL'], start=START, end=END)
#DATA = pdr.get_data_google(['SPY'], startdate=START, enddate=END)


def initialize(context):
    context.security = symbol('AAPL')

def handle_data(context, data):
    #order((symbol('AAPL'), 10))
    #record(AAPL=data.current(symbol('AAPL'), 'price'))
    MA1 = data[context.security].mavg(50)
    MA2 = data[context.security].mavg(100)
    date = str(data[context.security].datetime)[:10]
    current_price = data[context.security].price
    current_positions = context.portfolio.positions[symbol('AAPL')].amount
    cash = context.portfolio.cash
    value = context.portfolio.portfolio_value
    current_pnl = context.portfolio.pnl

    #code (this will come under handle_data function only)
    if (MA1 > MA2) and current_positions == 0:
        number_of_shares = int(cash/current_price)
        order(context.security, number_of_shares)
        record(date=date,MA1 = MA1, MA2 = MA2, Price= 
    current_price,status="buy",shares=number_of_shares,PnL=current_pnl,cash=cash,value=value)

    elif (MA1 < MA2) and current_positions != 0:
         order_target(context.security, 0)
         record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="sell",shares="--",PnL=current_pnl,cash=cash,value=value)

    else:
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="--",shares="--",PnL=current_pnl,cash=cash,value=value)

def main():
    print("Aqui porra")
    alg_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    perf_manual = alg_obj.run(DATA)
    perf_manual[["MA1","MA2","Price"]].plot()

if __name__ == '__main__':
    main()
