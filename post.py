import glob
import pandas as pd
from scipy.interpolate import interp1d

maxDischargeTemperatures = [-5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
maxDischargeRates = [0, 0, 0, 10.73759, 22.42149, 36.0174, 56.8107, 54.50289,
                     62.88506, 70.23952]
maxDischargePower = interp1d(maxDischargeTemperatures, maxDischargeRates,
                             kind="cubic")

files = glob.glob('./output/mult/*')

print(files)
profits = []

for f in files:
    data = pd.read_pickle(f)
    #print(data)

    cc =  data.loc[data['Q_dot'] > 0]
    cr =  data.loc[data['Q_dot'] < 0]
    cc = sum(cc['Q_dot'] / cc['COP'] * cc['dt * CoE'])
    cr = sum(-1 * cr['Q_dot'] / cr['COP'] * cr['dt * CoE'])
    #print(f[19:-10])
    profits.append([(cr - cc)/100, int(f[19:-10]), data['Loads(kWh)'].sum()])

profits.sort(key=lambda x:x[1])
print(profits)
# base1 = pd.read_pickle('./output/run1/0003_Base_Load_300_const.pkl')
# load1 = pd.read_pickle('./output/run1/0003_Load_1_300_const.pkl')
# load5 = pd.read_pickle('./output/run1/0003_Load_5_300_const.pkl')
# loadma = pd.read_pickle('./output/run1/0003_Load_MA_300_const.pkl')
# base2 = pd.read_pickle('./output/run2/0003_Base_Load_300_const.pkl')

# print(base1.columns)
# print("Base:   " ,base1['Loads(kWh)'].sum())
# print("Load_1: ",load1['Loads(kWh)'].sum())
# print("Load_5: ",load5['Loads(kWh)'].sum())
# print("Load_MA:",loadma['Loads(kWh)'].sum())
# print(base1)
# print(base2)
# print(base1[base1['COP'] != base2['COP']])
# files = glob.glob('./output/run1/*.pkl')

# # print(files)

# datas = []

# for f in files:
#     if 'dyn' in f:
#         if '300' in f:
#             if 'Base' in f:
#                 base = pd.read_pickle(f)
#             if 'DUoS' in f:
#                 fore = pd.read_pickle(f)
#         #data = pd.read_pickle(f)
#         #datas.append(data)

# #test = datas[0]
# print(base)
# maxdis = -1 * base['Loads(kW)'] * base['COP'] * maxDischargePower(base['Temp']) / 100
# print(fore)
# fore['True Price'] = base['dt * CoE']
# over = fore.loc[(fore['Mode'] == 'discharging') & (fore['Q_dot'] < maxdis) ]

# print(maxdis.describe())
# print(over)
# print(maxdis[over.index])
# fore.loc[over.index, 'Q_dot'] = over
# print(fore)
# soc = 0
# socs = []
# ind = 0
# for index, row in fore.iterrows():
#     if row['HH'] == 1:
#         ind += 1
#     if ind == 30:
#         soc = 0
#         ind = 0
#     soc += row['Q_dot'] / 2
#     socs.append(soc)

# fore['New SOC'] = socs
# print(fore)
# print(fore['SOC'].describe())
# print(fore["New SOC"].describe())
# print(fore[fore['New SOC'] > 300])

# cc = fore.loc[(fore['Q_dot'] > 0) & (fore['New SOC'] <= 310)]
# rc = fore.loc[(fore['Q_dot'] < 0) & (fore['New SOC'] >= 0)]
# cc = sum(cc['Q_dot'] / cc['COP'] * cc['True Price'])
# rc = sum(-1 * rc['Q_dot'] / rc['COP'] * rc['True Price'])

# print((rc - cc)/100)


# bc =  base.loc[base['Q_dot'] > 0]
# br =  base.loc[base['Q_dot'] < 0]
# bc = sum(bc['Q_dot'] / bc['COP'] * bc['dt * CoE'])
# br = sum(-1 * br['Q_dot'] / br['COP'] * br['dt * CoE'])
# print((br - bc)/100)
# # res = pd.DataFrame()

# for f in files:
#     if 'dyn' in f:
#         data = pd.read_pickle(f)
#         #print(data.loc[data['SOC'] > 300])
#         if 'Base' in f:
#             res['Date'] = data['Date']
#             res['HH'] = data['HH']
#             res['Temp'] = data['Temp']
#             res['Loads'] = data['Loads(kW)']
#             res['COP'] = data['COP']
#             res['Price'] = data['dt * CoE']
#             res['Q_dot'] = data['Q_dot']
#             res['Base Mode'] = data['Mode']
#             res['Base SOC'] = data['SOC']
#         if 'Load_1' in f:
#             res['L1 Mode'] = data['Mode']
#             res['L1 SOC'] = data['SOC']
#         if 'Load_MA' in f:
#             res['LMA Mode'] = data['Mode']
#         if 'Load_5' in f:
#             res['L5 Mode'] = data['Mode']
#         if 'Load_5H' in f:
#             res['L5H Mode'] = data['Mode']
#         if 'Price_1' in f:
#             res['P1 Mode'] = data['Mode']
            
# d = res[['Date', 'Base Mode', 'L1 Mode', 'Base SOC', 'L1 SOC']].loc[res['Base Mode'] != res['L1 Mode']]
# d = d[d['L1 SOC'] < 2]

# d.to_csv('test.csv')

#print(res.loc[res['Base Mode'] != res['L5 Mode']])

#print(res.loc[res['Base Mode'] != res['P1 Mode']])


# dyn300 = pd.DataFrame()
# const300 = pd.DataFrame()
# dyn1200 = pd.DataFrame()
# dyn300 = pd.DataFrame()
# #linprog/test/0003_Base_Load_300_const.pkl
# print(pd.read_pickle('./test/0003_Base_Load_300_const.pkl'))
# for f in files:
#     data = pd.read_pickle(f)
#     #print(data.loc[data['Loads(kW)'] < 80/data['COP']])
#     if '300' in f:
#         if 'const' in f:
#             if 'Base_Load' in f:
#                 const300['Date'] = data['Date']
#                 const300['Period'] = data['HH']
#                 const300['LBase_Q'] = data['Q_dot']
#                 const300['Price_Base'] = data['dt * CoE']
#                 const300['COP'] = data['COP']
#                 const300['DCOP'] = data['DCOP']
#                 #const300['LBase_CC'] = data['Q_dot'] / data['DCOP'] * data['dt * CoE']
#             elif 'Load_1' in f:
#                 const300['L1_Q'] = data['Q_dot']
#             elif 'Load_MA' in f:
#                 const300['LMA_Q'] = data['Q_dot']
#             elif 'Load_5' in f:
#                 const300['L5_Q'] = data['Q_dot']
#             elif 'Load_5H' in f:
#                 const300['L5H_Q'] = data['Q_dot']
#             elif 'Price_1' in f:
#                 const300['P1_Q'] = data['Q_dot']
#                 const300['Price_1'] = data['dt * CoE']
#             elif 'Price_DUoS' in f:
#                 const300['PD_Q'] = data['Q_dot']
#                 const300['Price_D'] = data['dt * CoE']
#             elif 'Pred' in f:
#                 const300['Pr_Q'] = data['Q_dot']
#             elif 'DUoS' in f:
#                 const300['PD_Q'] = data['Q_dot']                


# profs300 = pd.DataFrame()

# profs300['Date'] = const300['Date'].unique()
# base_daily = []
# L1_daily = []
# LMA_daily = []
# L5_daily = []
# P1_daily = []
# Pp_daily = []
# PD_daily = []

# for d in profs300['Date']:
#     dai = const300.loc[const300['Date'] == d]

#     bc =  dai.loc[dai['LBase_Q'] > 0]
#     br =  dai.loc[dai['LBase_Q'] < 0]
#     bc = sum(bc['LBase_Q'] / bc['COP'] * bc['Price_Base'])
#     br = sum(-1 * br['LBase_Q'] / br['COP'] * br['Price_Base'])

#     bc1 = dai.loc[dai['L1_Q'] > 0]
#     br1 = dai.loc[dai['L1_Q'] < 0]
#     bc1 = sum(bc1['L1_Q'] / bc1['COP'] * bc1['Price_Base'])
#     br1 = sum(-1 * br1['L1_Q'] / br1['COP'] * br1['Price_Base'])


#     bcma = dai.loc[dai['LMA_Q'] > 0]
#     brma = dai.loc[dai['LMA_Q'] < 0]
#     bcma = sum(bcma['LMA_Q'] / bcma['COP'] * bcma['Price_Base'])
#     brma = sum(-1 * brma['LMA_Q'] / brma['COP'] * brma['Price_Base'])

#     bc5 = dai.loc[dai['L5_Q'] > 0]
#     br5 = dai.loc[dai['L5_Q'] < 0]
#     bc5 = sum(bc5['L5_Q'] / bc5['COP'] * bc5['Price_Base'])
#     br5 = sum(-1 * br5['L5_Q'] / br5['COP'] * br5['Price_Base'])

#     bcp1 = dai.loc[dai['P1_Q'] > 0]
#     brp1 = dai.loc[dai['P1_Q'] < 0]
#     bcp1 = sum(bcp1['P1_Q'] / bcp1['COP'] * bcp1['Price_Base'])
#     brp1 = sum(-1 * brp1['P1_Q'] / brp1['COP'] * brp1['Price_Base'])


#     bcp = dai.loc[dai['Pr_Q'] > 0]
#     brp = dai.loc[dai['Pr_Q'] < 0]
#     bcp = sum(bcp['Pr_Q'] / bcp['COP'] * bcp['Price_Base'])
#     brp = sum(-1 * brp['Pr_Q'] / brp['COP'] * brp['Price_Base'])

#     bcd = dai.loc[dai['PD_Q'] > 0]
#     brd = dai.loc[dai['PD_Q'] < 0]
#     bcd = sum(bcd['PD_Q'] / bcd['COP'] * bcd['Price_Base'])
#     brd = sum(-1 * brd['PD_Q'] / brd['COP'] * brd['Price_Base'])

#     L5_daily.append((br5 - bc5)/100)
#     LMA_daily.append((brma - bcma)/100)
#     L1_daily.append((br1 - bc1)/100)
#     base_daily.append((br - bc)/100)
#     P1_daily.append((brp1 - bcp1)/100)
#     Pp_daily.append((brp - bcp)/100)
#     PD_daily.append((brd - bcd)/100)
#     #print(cc)
#     #print(rc)

#     #print(dai)
    
# #print(sum(daily))
# #print(months)
# profs300['Load_5_Profits'] = L5_daily
# profs300['Load_MA_Profits'] = LMA_daily
# profs300['Base_Profits'] = base_daily
# profs300['Load_1_Profits'] = L1_daily
# profs300['Price_1_Profits'] = P1_daily
# profs300['Pred_Profits'] = Pp_daily
# profs300['DUoS_proftis'] = PD_daily
# print(profs300.sum())

#profs300['Period'] = const300['Period']
#profs300['Base_Profs'] = 

#print(const300)




