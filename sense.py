import pandas as pd
import glob
import linprog as lp
import itertools
import dask
from dask.diagnostics import ProgressBar


if __name__ == '__main__':

    shops = glob.glob('./dat/*')


    start_date = '2019-01-31'
    end_date = '2020-01-01'

    starts = pd.date_range(start_date, end_date, freq='1M') - \
        pd.offsets.MonthBegin(1)
    starts = starts.to_list()
    ends = pd.date_range(start_date, end_date, freq='1M').to_list()


    pbar = ProgressBar()

    datas = [[lp.loadData(sh)[0], sh] for sh in shops]

    #print(datas)
    power = [300, 1200]
    mode = [True, False]

    params = list(itertools.product(power, mode))

    #print(params)

    runs = list(itertools.product(params, datas))

    #print(runs)

    dask.config.set(scheduler='processes')

    sheds = [[dask.delayed(lp.runModel)(d[1][0], starts, ends, maxCapacity=d[0][0], mod=d[0][1]), 
            d[0][0], d[0][1], d[1][1]] for d in runs]

    pbar.register()
    
    sheds = dask.compute(*sheds)

    for sch in sheds:
        model = '0003_'
        model += sch[3][sch[3].find("dat/")+4 : sch[3].find('.plk')]
        model += '_'+str(sch[1])
        if sch[2] == False:
            model += '_const'
        else:
            model += '_dyn'

        sch[0].to_pickle('./output/'+model+'.pkl')
        


