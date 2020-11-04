import glob
import pandas as pd

files = glob.glob('./test/*.pkl')

print(files)

for f in files:
    if 'const' in f:
        data = pd.read_pickle(f)
        name = f[7:-4]
        #name = name[f.find(name, 6): ]
        data.to_csv('./csvs/'+name+'.csv')

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


# profs300 = pd.DataFrame()

# profs300['Date'] = const300['Date'].unique()
# base_daily = []
# L1_daily = []
# LMA_daily = []
# L5_daily = []

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

#     L5_daily.append((br5 - bc5)/100)
#     LMA_daily.append((brma - bcma)/100)
#     L1_daily.append((br1 - bc1)/100)
#     base_daily.append((br - bc)/100)
#     #print(cc)
#     #print(rc)

#     #print(dai)
    
# #print(sum(daily))
# #print(months)
# profs300['Load_5_Profits'] = L5_daily
# profs300['Load_MA_Profits'] = LMA_daily
# profs300['Base_Profits'] = base_daily
# profs300['Load_1_Profits'] = L1_daily
# print(profs300.sum())

# #profs300['Period'] = const300['Period']
# #profs300['Base_Profs'] = 

# #print(const300)




