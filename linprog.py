# PCM schedule with linear programming (pyomo package)
# Michail Athanasakis for Flexible Power Systems Ltd.
# Last updated: 26 August 2020

import numpy as np
import numpy.matlib
#from pulp import *
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core.kernel.piecewise_library.transforms import piecewise
from random import randint
import operational_variables as ov
import functions as f
import icl_model as iclm
from datetime import datetime
from createHeatmap import createHeatmap

##############################################################################################


def setUp(start_date=ov.date, end_date=None, dt=ov.time_width, timestepBunch=48):
    # We start by creating all the necessary matrices for calculating the 
    # cost of delivering refrigeration at any point in time.

    # coe = cost of electricity at some half hour period (eg 00:30-01:00)
    # this returns a list of "DATE, HH, COE" for timeperiods in order.
    if end_date == None:
        coe = f.get_coe_by_date(start_date)
        bau_load = f.get_load_by_date(start_date)
    else:
        coe = f.concatenate_coe_by_date_range(start_date, end_date)
        bau_load = f.concatenate_load_by_date_range(start_date, end_date)
    
    if len(coe) != len(bau_load):
        raise Exception("Coe and bau load raw matrices not of same length. Sth wrong with date range.")
    # total timesteps is your total number of coe values
    s = len(coe)

    # Create a lower triangular matrix 
    TMatrix = np.zeros((s,s))   # lower triangular matrix
    for i in range(len(TMatrix[:])):
        for j in range(len(TMatrix[0,:])):
            if i >= j:
                TMatrix[i,j] = 1
            else:
                TMatrix[i,j] = 0
    
    # Here we create matrices that hold the COPs (coefficients of performance, ie efficiencies)
    # for the bau case (no pcm), and the system when PCM is discharging. The cop must be 
    # different for these cases because the physical system takes a complete different 
    # arrangement in these two functions.

    # During PCM charging, the cop is the same as bau (no PCM i.e. PCM on standby)

    # For each cop matrix, three entries will be put in each row: the date, the timeperiod,
    # and the cop.

    bauCOP = []               # bauCOP is the BAU cop (and charging COP) matrix
    dischargingCOP = []       # dischargingCOP is the cop matrix for a discharging PCM
    
    # also initialize the matrix that will hold only the coe matrices (no date and time) and 
    # that for the bau load
    Lambda = np.zeros((s, 1))
    bauLoad = np.zeros((s,1))

    for i in range(s):
        bauCOP.append([None,None,None])
        dischargingCOP.append([None,None,None])

    # two loops might be redundant but it's negligible runtime cost and it's easier to 
    # understand what's happening

    for i in range(s):

        Lambda[i] = round(coe[i][2], 2)         # keep coe matrix as a column s-by-1
        bauLoad[i] = round(bau_load[i][2], 2)   # same for bauLoad

        # remember that the coe matrix (not Lambda) also has dates and times, 
        # so copy from there
        bauCOP[i][0] = coe[i][0]            # date
        bauCOP[i][1] = coe[i][1]            # time
        #__, __, bauCOP[i][2] = iclm.calc_W(ov.T_PCM, \
        #      f.get_ambient_temperature(coe[i][0], coe[i][1]), ov.Q_mt, ov.Q_lt)
        bauCOP[i][2] = float(f.cop_from_temp(f.get_ambient_temperature(coe[i][0], coe[i][1])))
        #print(bauCOP[i][2])
        #print(f.get_ambient_temperature(coe[i][0], coe[i][1]))
        dischargingCOP[i][0] = coe[i][0]    # date
        dischargingCOP[i][1] = coe[i][1]    # time
        #_, __, temp = iclm.calc_W(ov.T_PCM, \
        #     f.get_ambient_temperature(coe[i][0], coe[i][1]), ov.Q_mt, ov.Q_lt, PCM=True, bypass_condenser=False)
        temp = f.dcop_from_temp(f.get_ambient_temperature(coe[i][0], coe[i][1]))
        #dischargingCOP[i][2] = temp - 1.5   # the current way of calculating d_COP is wrong
        #                                     # and tentative, and produces negative profits
        #                                     # so this is just to produce positive profit
        dischargingCOP[i][2] = temp
    # Since the COP when PCM is charging is the same as when the PCM is on standby (bau case)
    # we can just copy the matrix
    #chargingCOP = bauCOP

    #print(chargingCOP)

    # This is just a matrix where each item in Lambda is multiplied by dt.
    combinedLambda = dt * Lambda

    return coe, bauLoad, bauCOP, dischargingCOP, combinedLambda 

def  makeSched(coe, bauLoad, bauCOP, dischargingCOP, combinedLambda, timestepBunch=48, dt=ov.time_width):
    ##############################################################################################

    # Here is where the Pyomo package starts being used.
    model = ConcreteModel()

    kIndex= list(range(1,len(coe)+1))

    model.u = Var(kIndex, domain=Reals,  bounds=(ov.pcm.get_maxDischargeRate(), ov.pcm.get_maxChargeRate()))

    model.limits = ConstraintList()

    # create SOC next-day transfer constraint in bunches of multipleOf48
    multipleOf48 = int( len(coe) / timestepBunch )
    for j in range(multipleOf48):
        leftSlice = int(j*timestepBunch + 1)
        rightSlice = int((j+1)*timestepBunch)
        model.limits.add(
            (0, sum( model.u[k] for k in kIndex[leftSlice:rightSlice]), ov.pcm.get_maxCapacity())# SOC transf.
        )       
    
    # implement here the self-discharge option as you derived in the office
    # the self-discharge takes place at each timestep as SOC loss.
    # At any timestep k, the total self-discharge loss has been dt * lambda * k
    # where lambda is the self-discharge rate in kW and k the current timestep.
    leftLimit = -1*ov.pcm.get_initialSoc()/dt
    rightLimit = (ov.pcm.get_maxCapacity() - ov.pcm.get_initialSoc() ) / dt
    eta = ov.pcm.get_periodicDischargeRate() # by default at 0.001 kW

    
    J = 0
    for K in kIndex:
        T_amb = f.get_ambient_temperature(coe[K-1][0], coe[K-1][1]) # coe[K-1][0] and coe[K-1][1] are date and timeperiod respectively.
        model.limits.add( model.u[K] >= -1 * bauLoad[K-1,0])
        # constr. for dynamic (interpolated) discharge power
        model.limits.add( (-1*f.maxDischargePower(T_amb), model.u[K], ov.pcm.get_maxChargeRate()) )
        # this constraint has static max discharge rate
        #model.limits.add( (ov.pcm.get_maxDischargeRate(), model.u[K], ov.pcm.get_maxChargeRate()) )

        if J > 48:
            J = 0
        
        # def left_limit():    # nested function definition to impose a piece-wise constraint
        #     if sum(model.u[j] for j in range(1, K+1)) <= 0.5:
        #         return leftLimit
        #     elif sum(model.u[j] for j in range(1, K+1)) > 0.5:
        #         return leftLimit + J*eta

        # model.limits.add( (left_limit(), sum(model.u[j] for j in range(1, K+1)), rightLimit) ) # should make this piecewise
        model.limits.add( (leftLimit + J*eta, sum(model.u[j] for j in range(1, K+1)), rightLimit) ) # should make this piecewise
        J += 1

    # NEED to fix the Obj Func to employ the separate COPs. needs piecewise
    model.OBJ = Objective(
        expr=sum(
        # combinedLambda[K-1,0] * ( bauLoad[K-1,0] / bauCOP[K-1][2] + model.u[K] / bauCOP[K-1][2] ) for K in kIndex), 
        combinedLambda[K-1,0] * ( bauLoad[K-1,0] + model.u[K] / bauCOP[K-1][2] ) for K in kIndex),
            sense=minimize)

    
    opt = SolverFactory('glpk')
    opt.solve(model)

    #pyomo solve concrete_minimization.py --solver='glpk' --summary

    ############### MAKE SCHEDULE ##############################

    pcmSchedule = [["Date", "HH", "Q_dot", "Mode", "SOC", "dt * CoE", "BAU COP"]]

    m = 1
    for k in kIndex:
        #print(value(model.u[k]))

        if m > 48:
            m = 1
        pcmSchedule.append([coe[k-1][0], m, value(model.u[k]), "", 0, 0, 0, 0])
        if pcmSchedule[-1][2] == 0:
            pcmSchedule[-1][3] = "standby"
        elif pcmSchedule[-1][2] < 0:
            pcmSchedule[-1][3] = "discharging"
        elif pcmSchedule[-1][2] > 0:
            pcmSchedule[-1][3] = "charging"

        pcmSchedule[-1][2] = round(pcmSchedule[-1][2], 5)

        if k == 1:
            pcmSchedule[-1][4] = ov.pcm.get_initialSoc() + pcmSchedule[-1][2]*dt
        else:
            pcmSchedule[-1][4] = pcmSchedule[-2][4] + pcmSchedule[-1][2]*dt
        pcmSchedule[-1][4] = round(pcmSchedule[-1][4], 1)

        # check if SOC exceeds limits. Sometimes it might go to -0.001 or 300.001 so
        # we increase the limits by 1 kW to prevent false alarms
        if pcmSchedule[-1][4] < -1:
            print("PCM SOC below 0.")
        elif pcmSchedule[-1][4] > ov.pcm.get_maxCapacity()+1:
            print("PCM SOC above max capacity", ov.pcm.get_maxCapacity(),"kWh.")
        
        
        day = coe[k-1][0]
        hh = pcmSchedule[-1][1]
        pcmSchedule[-1][5] = combinedLambda[hh-1, 0]

        costElectricity = f.get_coe_by_date_and_time(coe[k-1][0], hh)
        pcmSchedule[-1][6] = round(costElectricity, 2)

        m += 1

    return pcmSchedule, kIndex

def calcProf(kIndex, start_date, end_date, chargingCOP, pcmSchedule, dt=ov.time_width, print_summary=False, print_schedule=False):
    chargingEvents = 0 
    dischargingEvents = 0
    totalChargeCost = 0
    totalReductionInCost = 0
    for k in kIndex:
        day = coe[k-1][0]
        hh = pcmSchedule[k][1]
        costElectricity = f.get_coe_by_date_and_time(coe[k-1][0], hh)
    #     ############ CALCULATE PROFITS #############
        for i in range(len(coe)):
            if chargingCOP[i][0] == day and chargingCOP[i][1] == hh:
                c_COP = chargingCOP[i][2]
                d_COP = dischargingCOP[i][2]
                break
        
        if pcmSchedule[k][2] > 0:
            chargingEvents += 1
            totalChargeCost += pcmSchedule[k][2] / c_COP * dt * costElectricity

        elif pcmSchedule[k][2] < 0:
            dischargingEvents += 1
            totalReductionInCost += -1 * pcmSchedule[k][2] / d_COP * dt * costElectricity

       
            
    totalProfit = round((totalReductionInCost - totalChargeCost)/100, 2)
    numberTrades = (chargingEvents + dischargingEvents) / 2

    if print_summary:
        print("The initial SOC was", ov.pcm.get_initialSoc()," kWh. The total profit for this schedule is", totalProfit, \
            "GBP with a total of", chargingEvents, "charging events and", \
                dischargingEvents, "discharging events.")
    
    if print_schedule: 
        if end_date == None:
            print("PCM schedule for", start_date, "with initial SOC", ov.pcm.get_initialSoc(), "kWh:")
        else:
            print("PCM schedule for period from", start_date, "to", end_date, "with initial SOC", ov.pcm.get_initialSoc(), "kWh:")
        for line in pcmSchedule:
            print(line)

    return totalProfit, chargingEvents, dischargingEvents,\
         numberTrades





if __name__ == "__main__":
    print("Start...")

    start1 = "02/01/2018"
    end1 = "01/02/2018"

    start2 = "02/02/2018"
    end2 = "01/03/2018"

    start3 = "02/03/2018"
    end3 = "01/04/2018"

    start4 = "02/04/2018"
    end4 = "01/05/2018"

    start5 = "02/05/2018"
    end5 = "01/06/2018"

    start6 = "02/06/2018"
    end6 = "01/07/2018"

    start7 = "02/07/2018"
    end7 = "01/08/2018"

    start8 = "02/08/2018"
    end8 = "01/09/2018"

    start9 = "02/09/2018"
    end9 = "01/10/2018"

    start10 = "02/10/2018"
    end10 = "01/11/2018"

    start11 = "02/11/2018"
    end11 = "01/12/2018"

    start12 = "02/12/2018"
    #end12 = "01/01/2019"
    end12 = "31/12/2018"


    starts = [start1, start2, start3, start4, start5, start6, start7, start8, start9, start10, start11, start12]
    ends = [end1, end2, end3, end4, end5, end6, end7, end8, end9, end10, end11, end12]
    #starts = [start12]
    #ends = [end12]

    schedsched = []
    profitsToDate = 0
    recording = []
    trad = 0

   

    for i in range(len(starts)):
        print(starts[i], ends[i])
        coe, bauLoad, bauCOP, dischargingCOP, combinedLambda = setUp(starts[i], ends[i])
        sched, kIndex = makeSched(coe, bauLoad, bauCOP, dischargingCOP, combinedLambda)
        profits, charges, discharges, trades = calcProf(kIndex, starts[i], ends[i], bauCOP, sched)
         
        #print(sched)
        schedsched += sched
        trad += trades
        profitsToDate += profits
        recording.append(
           [
               starts[i], ends[i], profits, charges, discharges, trad, profitsToDate
           ]
        )
    file = open("recordingyearylpyomo.txt", "w")
    file.write("Start date, End date, Profit GBP, Charges, Discharges, Trades, Profit to date GBP"+"\n")
    for line in recording:
        file.write(str(line)+"\n")
    file.close()

    createHeatmap(schedsched)






