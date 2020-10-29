# Source file for heatmap generation for linprog schedules
# Michail Athanasakis for Flexible Power Systems Ltd.
# Last updated: 12 August 2020


import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

def convert_tp_to_time(timeperiods):
	hour = 0
	deciminute = 3
	convertedHours = []

	for i in range(len(timeperiods)):
		if i % 2 == 0:
			deciminute = 3
		else:
			deciminute = 0
		if i % 2 == 1:
			hour += 1
		
		if hour < 10:
			temp = "0"+str(hour)+":"+str(deciminute)+"0"
		elif hour >= 10 and hour < 24:
			temp = str(hour)+":"+str(deciminute)+"0"
		elif hour == 24:
			hour = 0
			temp = "0"+str(hour)+":"+str(deciminute)+"0"
		
		convertedHours.append(temp)

	return convertedHours

def createHeatmap(schedule):

    dates = []
    timeperiods = list(range(1, 49))

    for i in range(len(schedule)):
        try:
            dates.index(schedule[i][0])
        except ValueError:
            dates.append(schedule[i][0])
    
    loads = np.zeros((len(timeperiods), len(dates)))

    for i, date in enumerate(dates):
        for j, tp in enumerate(timeperiods):
            for entry in schedule:
                if entry[0] == date and entry[1] == tp:
                    loads[j, i] = entry[2]
    
    # use loads, dates, and timeperiods as your data
    timeperiods = convert_tp_to_time(timeperiods)
    fig = go.Figure(data=go.Heatmap(
        z=loads,
        y=timeperiods,
        x=dates,
        hoverongaps=False,
        colorbar=dict(title='PCM Power (kW)') 
        ))


    fig.update_layout(
        title="PCM Schedule from "+str(dates[1])+" to "+str(dates[-1])
    )
    fig.show()



    #fig.write_image('./heatmap.png', width=1800, height=1000)

    return