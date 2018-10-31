# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 20:42:27 2018

@author: roy
"""

import pandas as pd, numpy as np

def year(x):
    results = [x[i].year for i in range(len(x))]
    return results

def mini(year):
    targe = data['Close'][pd.Series(years) == year].min()
    return targe

def bias_rate(current, ma):
    import numpy as np
    bias = (np.array(current) - np.array(ma))/np.array(ma)
    return bias

def location(x):
    import numpy as np 
    l = np.where(data['Close'] == x)[0]
    return l

years = year(x = data['Exchange Date'])

ma_years = data['Close'].rolling(window = 220).mean()
ma_season = data['Close'].rolling(window = 60).mean()
ma_month = data['Close'].rolling(window = 20).mean()

index = range(2007, 2019)
mini_point = [mini(index[i]) for i in range(len(index))]
y = [float(np.where(data['Close'] == mini_point[i])[0]) for i in range(len(index))]


ma_month_mini = [float(ma_month[location(mini_point[i])].values) for i in range(len(index))]
ma_season_mini = [float(ma_season[location(mini_point[i])].values) for i in range(len(index))] 
ma_year_mini = [float(ma_years[location(mini_point[i])].values) for i in range(len(index))] 

bias_rate_month = bias_rate(mini_point, ma_month_mini)
bias_rate_season = bias_rate(mini_point, ma_season_mini)
bias_rate_year = bias_rate(mini_point, ma_year_mini) 

ma_month_mini_next = [float(ma_month[location(mini_point[i]) + 20 ].values) for i in range(len(index))]
ma_season_mini_next = [float(ma_season[location(mini_point[i]) + 60 ].values) for i in range(len(index))] 
ma_year_mini_next = [float(ma_years[location(mini_point[i]) + 220 ].values) for i in range(len(index)-1)] 

real_month_next = [float(data['Close'][location(mini_point[i]) + 20].values) for i in range(len(index))]
real_season_next = [float(data['Close'][location(mini_point[i]) + 60].values) for i in range(len(index))]
real_year_next = [float(data['Close'][location(mini_point[i]) + 220].values) for i in range(len(index)-1)]

bias_rate_month_next  = bias_rate(real_month_next, ma_month_mini_next)
bias_rate_season_next  = bias_rate(real_season_next, ma_season_mini_next)
bias_rate_year_next  = bias_rate(real_year_next, ma_year_mini_next)

increaing_month_next = bias_rate(real_month_next, mini_point)
increaing_season_next = bias_rate(real_season_next, mini_point)
increaing_year_next = bias_rate(real_year_next, mini_point[0:11])

def increasing(days, array, rate):
    
    ma_year = array.rolling(window = 220).mean()
    ma_season = array.rolling(window = 60).mean()
    ma_month = array.rolling(window = 20).mean()
    
    l = len(array)
    start_end_loc = l - days
    start = array.iloc[range(start_end_loc)]
    end = array.iloc[range(days, l)]
    increasing_percent = pd.Series(end.values/start.values -1, name = 'increasing_percent')
    criteria_loc = np.where(increasing_percent <= rate)[0]
    
    def main(start0, start1, delta_diff, ma, value):
        delta_interval = delta_diff.iloc[start0:start1+1]
        real = value.iloc[start0:start1+1]
        mai = ma.iloc[start0:start1+1]
        c1 = delta_interval.diff().dropna()
        p0 = pd.Series([c1.iloc[i:i+2].prod() for i in range(len(c1)-1)])
        l1 = len(p0[p0<0])
        if l1 == 1:
            length = len(delta_interval)
            mini_real = real.min()
            mini_ma = mai.iloc[np.where(real == mini_real)[0]]
            delta = float((mini_ma - mini_real).values)
            count = 1
        else:
            length = 0
            delta = 0
            count = 0
        summary = [length, delta, count]
        return summary
    
    def criteria(delta_diff, ma, value):
        loc = np.where(delta_diff > 0)[0]
        loc2 = np.where(pd.Series(loc).diff()>1)[0]
        interval = [[loc[loc2[i] -1], loc[loc2[i]]] for i in range(len(loc2))]
        if len(loc)>=2 and len(interval)>=1:
            conclude = [main(interval[i][0], interval[i][1], delta_diff, ma, value) for i in range(len(interval))]
    
        else:
            conclude = [0, 0, 0]
            
        return conclude
    
    def track(downpoint, trackday):
        lag = downpoint - trackday
        if lag>=0:
            interval_real = array.iloc[lag: downpoint]
            interval_ma_month = ma_month.iloc[lag: downpoint]
            interval_ma_season = ma_season.iloc[lag: downpoint]
            interval_ma_year = ma_year.iloc[lag: downpoint]
            
            delta_month = interval_real - interval_ma_month
            delta_season = interval_real - interval_ma_season
            delta_year = interval_real - interval_ma_year
            
            s1 = criteria(delta_month, interval_ma_month, interval_real)
            s2 = criteria(delta_season, interval_ma_season, interval_real)
            s3 = criteria(delta_year, interval_ma_year, interval_real)
        else:
            s1 = [0, 0, 0]
            s2 = s1
            s3 = s1
        result = s1 + s2 + s3
        return result
    
    if len(criteria_loc)>=1:
        final_20 = [track(criteria_loc[i], 20) for i in range(len(criteria_loc))]
        final_60 = [track(criteria_loc[i], 60) for i in range(len(criteria_loc))]
        final_220 = [track(criteria_loc[i], 220) for i in range(len(criteria_loc))]
    else:
        final_20 = [0, 0, 0]
        final_60 = final_20
        final_220 = final_20
    
    def flatten(d):
        v = [[i] if not isinstance(i, list) else flatten(i) for i in d]
        return [i for b in v for i in b]
    
    final_20 =  np.array(flatten(final_20))
    final_60 = np.array(flatten(final_60))
    final_220 = np.array(flatten(final_220))
    
    l_20 = int(len(final_20)/3)
    l_60 = int(len(final_60)/3)
    l_220 = int(len(final_220)/3)
    
    final_20 = final_20.reshape(l_20, 3)
    final_60 = final_60.reshape(l_60, 3)
    final_220 = final_220.reshape(l_220, 3)
    
    summary_20 = np.sum(final_20, axis = 0)/l_20
    summary_60 = np.sum(final_60, axis = 0)/l_60
    summary_220 = np.sum(final_220, axis = 0)/l_220
    
    final_20 = np.unique(final_20, axis = 0)
    final_60 = np.unique(final_60, axis = 0)
    final_220 = np.unique(final_220, axis = 0)
    
    return summary_20[2], summary_60[2], summary_220[2], final_20, final_60, final_220

s0, s1, s2, x0, x1, x2 = increasing(days = 20, array = data['Close'], rate = -0.20)
u0, u1, u2, y0, y1, y2 = increasing(days = 60, array = data['Close'], rate = -0.20)
v0, v1, v2, z0, z1, z2 = increasing(days = 220, array = data['Close'], rate = -0.20)

