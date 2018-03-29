import os

import numpy  as np
import pandas as pd
import datetime

DEBUG=True # Set True to get trace messages

from zipline.utils.cli import maybe_show_progress

def viacsv(symbols, start=None,end=None):
    print("Here")
    tuSymbols = tuple(symbols)
    if DEBUG:
        print("Entering viacsv. {tuSymbols}".format(tuSymbols))
    
    # Define our custom ingest function
    def ingest(environ,
               asset_db_writer,
               minute_bar_writer,  # unused
               daily_bar_writer,
               adjustment_writer,
               calendar,
               cache,
               show_progress,
               output_dir,
               # pass these as defaults to make them 'nonlocal' in py2
               start=start,
               end=end):
        if DEBUG:
            print("entering ingest and creating blank dfMetadata")

        dfMetadata = pd.DataFrame(np.empty(len(tuSymbols), dtype=[
            ('start_date', 'datetime64[ns]'),
            ('end_date', 'datetime64[ns]'),
            ('auto_close_date', 'datetime64[ns]'),
            ('symbol', 'object'),
        ]))

        if DEBUG:
            print("dfMetadata",type(dfMetadata))
            print(dfMetadata.describe)
            print()

        # We need to feed something that is iterable - like a list or a generator -
        # that is a tuple with an integer for sid and a DataFrame for the data to
        # daily_bar_writer

        liData=[]
        iSid=0
        for S in tuSymbols:
            IFIL="~/workspace_financial_job/testando_zipline/csv/"+S+".csv"
            if DEBUG:
               print("S=",S,"IFIL=",IFIL)
            dfData=pd.read_csv(IFIL,index_col='Date',parse_dates=True).sort_index()
            if DEBUG:
               print("read_csv dfData",type(dfData),"length",len(dfData))
               print()
            dfData.rename(
                columns={
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume_(BTC)': 'volume btc',
                    'Volume_(Currency)': 'price',
                    'Weighted_Price': 'w price',
                },
                inplace=True,
            )
            dfData['volume']=dfData['volume']/1000
            liData.append((iSid,dfData))

            # the start date is the date of the first trade and
            start_date = dfData.index[0]
            if DEBUG:
                print("start_date",type(start_date),start_date)

            # the end date is the date of the last trade
            end_date = dfData.index[-1]
            if DEBUG:
                print("end_date",type(end_date),end_date)

            # The auto_close date is the day after the last trade.
            ac_date = end_date + pd.Timedelta(days=1)
            if DEBUG:
                print("ac_date",type(ac_date),ac_date)

            # Update our meta data
            dfMetadata.iloc[iSid] = start_date, end_date, ac_date, S

            iSid += 1

        if DEBUG:
            print("liData",type(liData),"length",len(liData))
            print(liData)
            print()
            print("Now calling daily_bar_writer")

        daily_bar_writer.write(liData, show_progress=False)

        # Hardcode the exchange to "YAHOO" for all assets and (elsewhere)
        # register "YAHOO" to resolve to the NYSE calendar, because the csv files
        # are for equities that traded per the NYSE calendar.
        dfMetadata['exchange'] = "YAHOO"

        if DEBUG:
            print("returned from daily_bar_writer")
            print("calling asset_db_writer")
            print("dfMetadata",type(dfMetadata))
            print(dfMetadata)
            print()

        # Not sure why symbol_map is needed
        symbol_map = pd.Series(dfMetadata.symbol.index, dfMetadata.symbol)
        if DEBUG:
            print("symbol_map",type(symbol_map))
            print(symbol_map)
            print()

        asset_db_writer.write(equities=dfMetadata)

        if DEBUG:
            print("returned from asset_db_writer")
            print("calling adjustment_writer")

        adjustment_writer.write()

        if DEBUG:
            print("returned from adjustment_writer")
            print("now leaving ingest function")

    if DEBUG:
       print("about to return ingest function")
    return ingest