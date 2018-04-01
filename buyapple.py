from zipline.api import record, order, symbol

def initialize(context):
    pass

def handle_data(context, data):
    order(symbol('AAPL'), 10)
    record(AAPL=data.current(symbol('AAPL'), 'price'))

def main():
    import pandas as pd
    perf = pd.read_pickle('buyapple.pickle') # read in perf DataFrame
    print(perf.__dict__)

    import matplotlib.pyplot as plt

    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')
    ax2 = plt.subplot(212, sharex=ax1)
    perf.AAPL.plot(ax=ax2)
    ax2.set_ylabel('AAPL stock price')
    plt.legend(loc=0)
    plt.show()


if __name__ == '__main__':
    main()