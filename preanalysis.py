import pandas as pd
import glob
from datetime import datetime, timedelta

files = glob.glob('./input/sense/*')
#print(files)

shops = []
el = []

start_date = '2019-02-01'
end_date = '2020-01-01'

elect = glob.glob('./input/elect/*')
#print(elect)

for e in elect:
    df = pd.read_csv(e)
    df['date'] = pd.to_datetime(df['date'])
    del df['from']
    del df['to']
    del df['region_name']
    del df['code']
    del df['gsp']
    del df['unit_rate_excl_vat']
    df['Price'] = df['unit_rate_incl_vat']
    del df['unit_rate_incl_vat']

    mask = (df['date'] >= start_date) & (df['date'] < end_date)
    el.append(df.loc[mask].reset_index(drop=True))



for file in files:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'] >= start_date) & (df['Date'] < end_date)
    shops.append(df.loc[mask].reset_index(drop=True))

integers = list(range(1, 49)) * 334

first = pd.DataFrame()
first['Date'] = shops[0]['Date']
first['Loads'] = shops[0]['LTPackElectricity']
first['Temp'] = shops[0]['Temperature'].fillna(method='ffill')
first = first.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': first._get_value(4273, 'Loads'), 'Temp' : first._get_value(4273, 'Temp')}, ignore_index=True)
first = first.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': first._get_value(4273, 'Loads'), 'Temp' : first._get_value(4273, 'Temp')}, ignore_index=True)
first = first.sort_values(by='Date')
first = first.reset_index(drop=True)
first['Period'] = integers
first['Price'] = el[2]['Price']
first['Date'] = first['Date'].dt.date

first.to_pickle('./dat/2288.pkl')

second = pd.DataFrame()
second['Date'] = shops[1]['Date']
second['Loads'] = shops[1]['ITPackElectricity']
second['Temp'] = shops[1]['Temperature'].fillna(method='ffill')
second = second.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
second = second.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
second = second.sort_values(by='Date')
second = second.reset_index(drop=True)
second['Period'] = integers
second['Price'] = el[0]["Price"]
second['Date'] = second['Date'].dt.date

second.to_pickle('./dat/0003.pkl')


third = pd.DataFrame()
third['Date'] = shops[2]['Date']
third['Loads'] = shops[2]['DTPackElectricity']
third['Temp'] = shops[2]['Temperature'].fillna(method='ffill')
third = third.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': third._get_value(4273, 'Loads'), 'Temp' : third._get_value(4273, 'Temp')}, ignore_index=True)
third = third.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': third._get_value(4273, 'Loads'), 'Temp' : third._get_value(4273, 'Temp')}, ignore_index=True)
third = third.sort_values(by='Date')
third = third.reset_index(drop=True)
third['Period'] = integers
third['Price'] = el[1]['Price']
third['Date'] = third['Date'].dt.date

third.to_pickle('./dat/2318.pkl')



# # print(second)
# # print(third)

# storage_cap = [300, 1200]
# dis_type = [False, True]
# shops = [first, second, third]



# starts= pd.date_range(start_date, end_date , freq='1M')-pd.offsets.MonthBegin(1)
# ends = pd.date_range(start_date, end_date , freq='1M')
# print(starts)
# print(ends)