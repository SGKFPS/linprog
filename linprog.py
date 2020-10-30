""" Dispatch Algorithm v2. Linear programming implementation using 'pyomo'
Flexible Power Systems Ltd.
"""
import numpy as np
from datetime import datetime
from createHeatmap import createHeatmap
import pandas as pd
import glob
from scipy.interpolate import interp1d
from pyomo.environ import *
from pyomo.opt import SolverFactory
from createHeatmap import createHeatmap


""" The set of constants used in the tool.
Defined as globals they represent parameters of the PCM,
                                  initial conditions and
                                  parameters for analysis.
"""
maxDischargeRate = -80
maxChargeRate = 80
maxCapacity = 300
periodicDischargeRate = 0.001
dt = 0.5
initialSoc = 0

""" CoP for the refrigeration cycle is handled with data from look-up tables.
The current implementation imports them from csv files.
TODO: create a function that sets the COPs - enable analysis with different
      COPs.
"""
cop_data = []
cop_file_loc = "./input/20-09.PCM.ICLv2_COP_general.01.HC.csv"

cop_file = open(cop_file_loc, 'r')
for i, line in enumerate(cop_file):
    if i == 0 or i == 1:
        continue
    words = line.split(",")
    cop_data.append([float(words[0]), float(words[1].strip('\n'))])


cop_data = np.array(cop_data)
# Set interpolation function to get COP value for a given ambient temperature
get_cop = interp1d(cop_data[:, 0], cop_data[:, 1], kind='cubic')

dcop_data = []
dcop_file_loc = "./input/20-09.PCM.ICLv2_COP_maxPCM_mode.01.HC.csv"
dcop_file = open(cop_file_loc, 'r')
for i, line in enumerate(dcop_file):
    if i == 0 or i == 1:
        continue
    words = line.split(",")
    dcop_data.append([float(words[0]), float(words[1].strip('\n'))])


dcop_data = np.array(dcop_data)
# Set interpolation function to get DCOP value for a given ambient temperature
get_dcop = interp1d(dcop_data[:, 0], dcop_data[:, 1], kind='cubic')


# Create interpolation function for maxDischargePower
maxDischargeTemperatures = [-5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
maxDischargeRates = [0, 0, 0, 10.73759, 22.42149, 36.0174, 56.8107, 54.50289,
                     62.88506, 70.23952]
maxDischargePower = interp1d(maxDischargeTemperatures, maxDischargeRates,
                             kind="cubic")

# ====================================================================


def loadData(filename, freq):
    """ Load and prepare data for analysis.
    Computes Lambda, COP and COE and defines the frequency in the analysis
    with freq.

    Keyword arguments:
    filename -- the file that contains the dataset in pickle format
    freq -- the frequency to be used in pd.date_range
    """
    data = pd.read_pickle(filename)

    start_date = data.iloc[0, 0]
    end_date = data.iloc[-1, 0]

    starts = pd.date_range(start_date, end_date, freq=freq) - \
        pd.offsets.MonthBegin(1)
    starts = starts.to_list()
    ends = pd.date_range(start_date, end_date, freq=freq).to_list()

    data['Lambda'] = data['Price'] * dt
    data['COP'] = data['Temp'].apply(lambda x: get_cop(x))
    data['DCOP'] = data['Temp'].apply(lambda x: get_dcop(x))

    return data, starts, ends


def runModel(data, starts, ends, timestep=48):
    """ Run the model and compute the schedule according to the optimized
    PCM charge/dicharge values.

    Keyword arguments:
    data -- DataFrame that contains the data to be used in the modelling
    starts -- list of start dates for the analysis
    ends -- list of end dates for the analysis
    timestep -- number of timesteps in day (default 48)
    """

    schedule = pd.DataFrame(columns=["Date", "HH", "Q_dot", "Mode", "SOC",
                                     "dt * CoE", "BAU COE"])

    for (start, end) in zip(starts, ends):
        # pick subset of the dataset according to the dates
        dat = data.loc[(data['Date'] >= start) & (data['Date'] <= end)]
        dat = dat.reset_index(drop=True)

        # define pyomo model
        model = ConcreteModel()

        # define index for model
        Kindex = dat.index.values.tolist()
        for i in range(len(Kindex)):
            Kindex[i] += 1

        # define model parameters
        model.u = Var(Kindex, domain=Reals, bounds=(maxDischargeRate,
                                                    maxChargeRate))

        model.limits = ConstraintList()

        multiple48 = int(len(Kindex) / timestep)
        for j in range(multiple48):
            leftslice = int(j*timestep)
            rightslice = int((j+1)*timestep)
            # create SOC next-day transfer constraint
            model.limits.add(
                (0, sum(model.u[k] for k in Kindex[leftslice:rightslice]),
                 maxCapacity)
            )

        # define limits for PCM
        leftLimit = -1 * initialSoc / dt
        rightLimit = (maxCapacity - initialSoc) / dt
        # self-discharge option
        eta = periodicDischargeRate

        J = 0

        # get lists of data to be used in the model definition
        temps = dat['Temp'].to_list()
        bau = (dat['Loads'] / 0.5).to_list()
        cop = dat['COP'].to_list()
        lamb = dat['Lambda'].to_list()

        for k in Kindex:
            model.limits.add(model.u[k] >= -1 * bau[k-1])
            model.limits.add((-1 * maxDischargePower(temps[k-1]), model.u[k],
                             maxChargeRate))
            model.limits.add((maxDischargeRate, model.u[k], maxChargeRate))

            if J > 48:
                J = 0

            model.limits.add((leftLimit + J * eta,
                              sum(model.u[j] for j in range(1, k+1)),
                              rightLimit))
            J += 1

        # print("Added all limits")

        model.OBJ = Objective(
            expr=sum(
                    lamb[k-1] * (bau[k-1] + model.u[k] / cop[k-1])
                    for k in Kindex), sense=minimize
            )

        # print('Defined Objectice function')
        opt = SolverFactory('glpk')
        # print("Running the model: ")

        opt.solve(model)

        # grab date, HH and price data
        dates = dat['Date']
        period = dat['Period']
        price = dat['Price']

        for k in Kindex:
            res = round(value(model.u[k]), 5)
            mode = ''
            soc = 0

            if res == 0:
                mode = 'standby'
            elif res < 0:
                mode = 'discharging'
            elif res > 0:
                mode = 'charging'

            if k == 1:
                soc = initialSoc + res * dt
            else:
                soc += res * dt

            soc = round(soc, 1)
            # if soc < -1:
            #     print('PCM SOC bellow 0.')
            # elif soc > maxCapacity:
            #     print('PCM SOC above max capacity, ', maxCapacity, " kWh.")

            # "Date", "HH", "Q_dot", "Mode", "SOC", "dt * CoE", "BAU COE"
            schedule = schedule.append({'Date': dates[k-1], 'HH': period[k-1],
                                        'Q_dot': res, 'Mode': mode, 'SOC': soc,
                                        'dt * CoE': lamb[k-1],
                                        'BAU COE': price[k-1]},
                                       ignore_index=True)

    return schedule


if __name__ == "__main__":

    shop = glob.glob("./dat/0003.pkl")

    data, starts, ends = loadData(shop[0], '1M')

    print(data)

    sched = runModel(data, starts, ends)

    heat = sched.values

    print(sched)
    print(heat)
    print(heat[0, 0])

    createHeatmap(heat)
