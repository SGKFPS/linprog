import pandas as pd
import glob
import linprog as lp
import itertools
import dask
from dask.diagnostics import ProgressBar


if __name__ == '__main__':

    shops = glob.glob('./dat/0003/*')


    start_date = '2019-01-31'
    end_date = '2020-01-01'

    starts = pd.date_range(start_date, end_date, freq='1M') - \
        pd.offsets.MonthBegin(1)
    starts = starts.to_list()
    #starts = [starts[0]]
    ends = pd.date_range(start_date, end_date, freq='1M').to_list()
    #print(ends)
    #ends = [ends[-1]]

    #print(starts)
    #print(ends)

    pbar = ProgressBar()


    print("Begin loading input files...")
    datas = [[lp.loadData(sh)[0], sh] for sh in shops]

    #print(datas)
    power = [300]
    mode = [False, True]

    params = list(itertools.product(power, mode))

    #print(params)

    runs = list(itertools.product(params, datas))

    #print(runs)

    dask.config.set(scheduler='processes')

    sheds = [[dask.delayed(lp.runModel)(d[1][0], starts, ends, maxCapacity=d[0][0], mod=d[0][1]), 
            d[0][0], d[0][1], d[1][1]] for d in runs]


    
    print("Running "+str(len(sheds))+" models!")

    pbar.register()
    sheds = dask.compute(*sheds)

    for sch in sheds:
        model = '0003_'
        model += sch[3][sch[3].find("0003/")+5 : sch[3].find('.plk')]
        #print(model)
        model += '_'+str(sch[1])
        #print(sch[3])
        #model += sch[3][sch[3].find("dat/")+9 : sch[3].find('.plk')]
        if sch[2] == False:
            model += '_const'
        else:
            model += '_dyn'
        #print(model)
        sch[0].to_pickle('./output/out/'+model+'.pkl')
        


