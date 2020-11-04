import pandas as pd
import glob
from datetime import datetime, timedelta


start_date = '2019-01-31'
end_date = '2020-01-01'
files = glob.glob('./input/sense/*xlsx')

print(files)
data = []

for f in files:
    dat = pd.read_excel(f)
    data.append(dat)


#print(data[-1])
#dat = data[-1]

el2318 = data[0]
el0003 = data[1]
load0003 = data[2]
load2318 = data[3]

load0003 = load0003.drop_duplicates(subset=['Date'])
load2318 = load2318.drop_duplicates(subset=['Date'])


mask = (load0003['Date'] >= start_date) & (load0003['Date'] < end_date)
load0003 = load0003.loc[mask].reset_index(drop=True)

mask = (load2318['Date'] >= start_date) & (load2318['Date'] < end_date)
load2318 = load2318.loc[mask].reset_index(drop=True)



mask = (el2318['SettlementDate'] >= start_date) & (el2318['SettlementDate'] < end_date)
el2318 = el2318.loc[mask].reset_index(drop=True)



mask = (el0003['Date and Time'] >= start_date) & (el0003['Date and Time'] < end_date)
el0003 = el0003.loc[mask].reset_index(drop=True)

print(load2318)

# #dup = dat[dat.duplicated(['Date'])]

# #print(dup)

# date_set= set(load2318['Date'])
# one_day = timedelta(minutes=30)

# test_date = datetime.strptime(start_date, "%Y-%m-%d")
# missing_dates=[]
# while test_date < datetime.strptime(end_date, "%Y-%m-%d"):
#     if test_date not in date_set:
#         missing_dates.append(test_date)
#     test_date += one_day

# print(missing_dates)

""" Store 0003 refrigeration loads """
load0003 = load0003.append({'Date' : pd.Timestamp('2019-03-31 01:00:00')}, ignore_index=True)
load0003 = load0003.append({'Date' : pd.Timestamp('2019-03-31 01:30:00')}, ignore_index=True)
load0003 = load0003.sort_values(by='Date')
load0003 = load0003.reset_index(drop=True)

#print(load0003.columns)

load0003['Predicted ITPack Model 1'] = load0003['Predicted ITPack Model 1'].fillna(method='ffill')
load0003['Predicted ITPack Flat (Monthly Average)'] = load0003['Predicted ITPack Flat (Monthly Average)'].fillna(method='ffill')
load0003['ITPackElectricity_Observed'] = load0003['ITPackElectricity_Observed'].fillna(method='ffill')
load0003['Predicted ITPack Model 5'] = load0003['Predicted ITPack Model 5'].fillna(method='ffill')
load0003['Predicted ITPack Model 5H (+Humidity)'] = load0003['Predicted ITPack Model 5H (+Humidity)'].fillna(method='ffill')

#print(load0003)


""" Store 2318 refrigeration loads """
load2318 = load2318.append({'Date' : pd.Timestamp('2019-03-31 01:00:00')}, ignore_index=True)
load2318 = load2318.append({'Date' : pd.Timestamp('2019-03-31 01:30:00')}, ignore_index=True)
load2318 = load2318.sort_values(by='Date')
load2318 = load2318.reset_index(drop=True)

#print(load2318.columns)

load2318['Predicted DTPack Model 1'] = load2318['Predicted DTPack Model 1'].fillna(method='ffill')
load2318['Predicted DTPack Flat (Monthly Average)'] = load2318['Predicted DTPack Flat (Monthly Average)'].fillna(method='ffill')
load2318['DTPackElectricity_Observed'] = load2318['DTPackElectricity_Observed'].fillna(method='ffill')
load2318['Predicted DTPack Model 5'] = load2318['Predicted DTPack Model 5'].fillna(method='ffill')
load2318['Predicted DTPack Model 5H (+Humidity)'] = load2318['Predicted DTPack Model 5H (+Humidity)'].fillna(method='ffill')


# print(load2318)



f3 = './input/sense/20-06.SSL.0003_historic_cleaned_loads.01.BF.csv'

df = pd.read_csv(f3)
df['Date'] = pd.to_datetime(df['Date'])
mask = (df['Date'] >= start_date) & (df['Date'] < end_date)
temp0003 = df.loc[mask].reset_index(drop=True)

temp0003['Temperature'] = temp0003['Temperature'].fillna(method='ffill')
temp0003 = temp0003.append({'Date' : pd.Timestamp('2019-03-31 01:00:00')}, ignore_index=True)
temp0003 = temp0003.append({'Date' : pd.Timestamp('2019-03-31 01:30:00')}, ignore_index=True)
temp0003['Temperature'] = temp0003['Temperature'].fillna(method='ffill')
temp0003['Temperature'] = temp0003['Temperature'].fillna(method='ffill')
temp0003 = temp0003.sort_values(by='Date')
temp0003 = temp0003.reset_index(drop=True)

#print(temp0003.isna().sum())

load0003['Temperature'] = temp0003['Temperature']



f2 = './input/sense/20-06.SSL.2288_historic_cleaned_loads.01.BF.csv'

df = pd.read_csv(f2)
df['Date'] = pd.to_datetime(df['Date'])
mask = (df['Date'] >= start_date) & (df['Date'] < end_date)
temp2318 = df.loc[mask].reset_index(drop=True)

temp2318['Temperature'] = temp2318['Temperature'].fillna(method='ffill')
temp2318 = temp2318.append({'Date' : pd.Timestamp('2019-03-31 01:00:00')}, ignore_index=True)
temp2318 = temp2318.append({'Date' : pd.Timestamp('2019-03-31 01:30:00')}, ignore_index=True)
temp2318['Temperature'] = temp2318['Temperature'].fillna(method='ffill')
temp2318['Temperature'] = temp2318['Temperature'].fillna(method='ffill')
temp2318 = temp2318.sort_values(by='Date')
temp2318 = temp2318.reset_index(drop=True)


load2318['Temperature'] = temp2318['Temperature']

print(load2318)

print(el0003.isna().sum())

sh0003 = pd.DataFrame()

integers = list(range(1, 49)) * 335

sh0003['Date'] = temp0003['Date'].dt.date
sh0003['Period'] = integers
sh0003['Temp'] = load0003['Temperature']
sh0003['Base Loads'] = load0003['ITPackElectricity_Observed']
sh0003['Predicted Loads 1'] = load0003['Predicted ITPack Model 1']
sh0003['Predicted Loads MA'] = load0003['Predicted ITPack Flat (Monthly Average)']
sh0003['Predicted Loads 5'] = load0003['Predicted ITPack Model 5']
sh0003['Predicted Loads 5H'] = load0003['Predicted ITPack Model 5H (+Humidity)']
sh0003['Base Price'] = el0003['Agile_excl_vat']
sh0003['Predicted Price 1'] = el0003['Total_excl_triad']
sh0003['Predicted DUoS'] = el0003['DUoS']

print(sh0003.isna().sum())

sh2318 = pd.DataFrame()

sh2318['Date'] = temp2318['Date'].dt.date
sh2318['Period'] = integers
sh2318['Temp'] = load2318['Temperature']
sh2318['Base Loads'] = load2318['DTPackElectricity_Observed']
sh2318['Predicted Loads 1'] = load2318['Predicted DTPack Model 1']
sh2318['Predicted Loads MA'] = load2318['Predicted DTPack Flat (Monthly Average)']
sh2318['Predicted Loads 5'] = load2318['Predicted DTPack Model 5']
sh2318['Predicted Loads 5H'] = load2318['Predicted DTPack Model 5H (+Humidity)']
sh2318['Base Price'] = el2318['Agile_excl_vat']
sh2318['Predicted Price 1'] = el2318['Total_excl_triad']

print(sh2318.isna().sum())
print(sh2318)

#sh0003.to_pickle('./dat/0003_sense.pkl')


dats = ['Base_Load', 'Load_1', 'Load_MA', 'Load_5', 'Load_5H', 'Price_1', 'Price_DUoS', 'Pred']
datasets = [pd.DataFrame() for i in range(len(dats))]

print(datasets)

for (d, n) in zip(datasets, dats):
    d['Date'] = sh0003['Date']
    d['Period'] = sh0003['Period']
    d['Temp'] = sh0003['Temp']
    if n == 'Base_Load':
        d['Loads'] = sh0003['Base Loads']
        d['Price'] = sh0003['Base Price']
    elif n == 'Load_1':
        d['Loads'] = sh0003['Predicted Loads 1']
        d['Price'] = sh0003['Base Price']
    elif n == 'Load_MA':
        d['Loads'] = sh0003['Predicted Loads MA']
        d['Price'] = sh0003['Base Price']
    elif n == 'Load_5':
        d['Loads'] = sh0003['Predicted Loads 5']
        d['Price'] = sh0003['Base Price']
    elif n == 'Load_5H':
        d['Loads'] = sh0003['Predicted Loads 5H']
        d['Price'] = sh0003['Base Price']
    elif n == 'Price_1':
        d['Loads'] = sh0003['Base Loads']
        d['Price'] = sh0003['Predicted Price 1']
    elif n == 'Pred':
        d['Loads'] = sh0003['Predicted Loads 5']
        d['Price'] = sh0003['Predicted Price 1']
    elif n == 'Price_DUoS':
        d['Loads'] = sh0003['Base Loads']
        d['Price'] = sh0003['Predicted DUoS']
    d.to_pickle('./dat/'+n+'.plk')

print(datasets)

#print(el0003[el0003.isnull().any(axis=1)])

# files = glob.glob('./input/sense/*')
# #print(files)

# shops = []
# el = []

# start_date = '2019-01-01'
# end_date = '2020-01-01'

# #elect = glob.glob('./input/elect/*')
# # #print(elect)

# dis = glob.glob('./input/dis/*')
# #print(dis)

# for d in dis:
#     df = pd.read_csv(d, dtype={'SettlementPeriod': int})
#     df = df[df['Name'] == 'South Eastern England']
#     del df['Name']
#     del df['GSPZone']
#     del df['DUoS_band']
#     del df['DUoS']
#     del df['BSUoS']
#     del df['Wholesale']
#     del df['Triad']
#     del df['LLF']
#     del df['OffTaking_TLF']
#     del df['Delivering_TLF']
#     df = df.reset_index(drop=True)
#     df['SettlementDate'] = pd.to_datetime(df['SettlementDate'])

#     #print(df)

#     mask = (df['SettlementDate'] >= start_date) & (df['SettlementDate'] < end_date)
#     #print(df.loc[mask])
#     #print(df[df.isna().any(axis=1)])
#     el.append(df.loc[mask].reset_index(drop=True))

# # for e in elect:
# #     df = pd.read_csv(e)
# #     df['date'] = pd.to_datetime(df['date'])
# #     del df['from']
# #     del df['to']
# #     del df['region_name']
# #     del df['code']
# #     del df['gsp']
# #     del df['unit_rate_excl_vat']
# #     df['Price'] = df['unit_rate_incl_vat']
# #     del df['unit_rate_incl_vat']
# #     print(df)
# #     mask = (df['date'] >= start_date) & (df['date'] < end_date)
# #     el.append(df.loc[mask].reset_index(drop=True))



# for file in files:
#     df = pd.read_csv(file)
#     df['Date'] = pd.to_datetime(df['Date'])
#     mask = (df['Date'] >= start_date) & (df['Date'] < end_date)
#     shops.append(df.loc[mask].reset_index(drop=True))

# integers = list(range(1, 49)) * 365 #334

# # first = pd.DataFrame()
# # first['Date'] = shops[0]['Date']
# # first['Loads'] = shops[0]['LTPackElectricity']
# # first['Temp'] = shops[0]['Temperature'].fillna(method='ffill')
# # first = first.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': first._get_value(4273, 'Loads'), 'Temp' : first._get_value(4273, 'Temp')}, ignore_index=True)
# # first = first.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': first._get_value(4273, 'Loads'), 'Temp' : first._get_value(4273, 'Temp')}, ignore_index=True)
# # first = first.sort_values(by='Date')
# # first = first.reset_index(drop=True)
# # first['Period'] = integers
# # first['Price'] = el[2]['Price']
# # first['Date'] = first['Date'].dt.date

# # first.to_pickle('./dat/2288.pkl')

# second = pd.DataFrame()
# second['Date'] = shops[1]['Date']
# second['Loads'] = shops[1]['ITPackElectricity']
# second['Temp'] = shops[1]['Temperature'].fillna(method='bfill')
# #print(pd.date_range(start = start_date, end = end_date ).difference(second.index))

# # date_set=set(second['Date'])
# # one_day = timedelta(minutes=30)

# # test_date = datetime.strptime(start_date, "%Y-%m-%d")
# # missing_dates=[]
# # while test_date < datetime.strptime(end_date, "%Y-%m-%d"):
# #     if test_date not in date_set:
# #         missing_dates.append(test_date)
# #     test_date += one_day

# # print(missing_dates)
# # second = second.append({'Date' : pd.Timestamp('2018-01-01 00:00:00'), 'Loads': second._get_value(0, 'Loads'), 'Temp' : second._get_value(0, 'Temp')}, ignore_index=True)
# # second = second.append({'Date' : pd.Timestamp('2018-03-25 01:00:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
# # second = second.append({'Date' : pd.Timestamp('2018-03-25 01:30:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
# second = second.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
# second = second.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': second._get_value(4273, 'Loads'), 'Temp' : second._get_value(4273, 'Temp')}, ignore_index=True)
# second = second.sort_values(by='Date')
# second = second.reset_index(drop=True)
# second['Temp'] = second['Temp'].fillna(method='ffill')
# second['Period'] = integers
# second['Price'] = el[0]["Total_excl_triad"]
# second['Date'] = second['Date'].dt.date
# # second['Price'] = second['Price'].fillna(method='ffill')

# #print(second[second.isna().any(axis=1)])
# second.to_pickle('./dat/0003_2018.pkl')


# # third = pd.DataFrame()
# # third['Date'] = shops[2]['Date']
# # third['Loads'] = shops[2]['DTPackElectricity']
# # third['Temp'] = shops[2]['Temperature'].fillna(method='ffill')
# # third = third.append({'Date' : pd.Timestamp('2019-03-31 01:00:00'), 'Loads': third._get_value(4273, 'Loads'), 'Temp' : third._get_value(4273, 'Temp')}, ignore_index=True)
# # third = third.append({'Date' : pd.Timestamp('2019-03-31 01:30:00'), 'Loads': third._get_value(4273, 'Loads'), 'Temp' : third._get_value(4273, 'Temp')}, ignore_index=True)
# # third = third.sort_values(by='Date')
# # third = third.reset_index(drop=True)
# # third['Period'] = integers
# # third['Price'] = el[1]['Price']
# # third['Date'] = third['Date'].dt.date

# # third.to_pickle('./dat/2318.pkl')



# # # print(second)
# # # print(third)

# # storage_cap = [300, 1200]
# # dis_type = [False, True]
# # shops = [first, second, third]



# # starts= pd.date_range(start_date, end_date , freq='1M')-pd.offsets.MonthBegin(1)
# # ends = pd.date_range(start_date, end_date , freq='1M')
# # print(starts)
# # print(ends)