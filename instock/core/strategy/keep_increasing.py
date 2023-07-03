#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import threading

import numpy as np
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


# 持续上涨（MA30向上）
# 均线多头
# 1.30日前的30日均线<20日前的30日均线<10日前的30日均线<当日的30日均线
# 3.(当日的30日均线/30日前的30日均线)>1.2
def check(code_name, data, date=None, threshold=5):
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False
    data.loc[:, 'cci'] = tl.CCI(data['high'], data['low'], data['close'], timeperiod=14)
    data['cci'].values[np.isnan(data['cci'].values)] = 0.0
    last_3_days_cci = sum(data.tail(3)['cci'] > 100)

    ma_periods = [5, 10, 20, 30]
    for period in ma_periods:
        ma_column = f'ma{period}'
        data.loc[:, ma_column] = tl.MA(data['close'].values, timeperiod=period)
        data[ma_column].values[np.isnan(data[ma_column].values)] = 0.0

    data = data.tail(n=threshold)

    # step1 = round(threshold / 3)
    # step2 = round(threshold * 2 / 3)
    last_ma5 = data.iloc[-threshold:]['ma5'].tolist()
    last_ma10 = data.iloc[-threshold:]['ma10'].tolist()
    last_ma20 = data.iloc[-threshold:]['ma20'].tolist()
    last_ma30 = data.iloc[-threshold:]['ma30'].tolist()
    lock = threading.Lock()
    consecutive_days = 0
    for i in range(5):
     with lock:
        if last_ma5[i] > last_ma10[i] and (last_ma10[i] > last_ma20[i] or last_ma10[i] > last_ma30[i]):
                consecutive_days += 1
                crossover_values = last_ma5[i] - last_ma10[i]
                if consecutive_days >= 1 and consecutive_days <= 3 and crossover_values > 0.05 and crossover_values < 0.3 \
                        and last_3_days_cci >= 2:
                    return True
    return False
    # ma5>ma10 and ma10>ma20 or ma10>ma30
    # if data.iloc[-4]['ma5'] > data.iloc[-3]['ma10'] and data.iloc[-3]['ma10'] > data.iloc[-2]['ma20'] \
    #         or data.iloc[-3]['ma10'] > data.iloc[-1]['ma30']:
    #     return True
    # # if data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] < \
    # #         data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and data.iloc[-1]['ma30'] > 1.2 * data.iloc[0]['ma30']:
    # #     return True
    # else:
    #     return False
