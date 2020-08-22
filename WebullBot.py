#WeBull Trading Bot, by Jacob Amaral
#Youtube : Jacob Amaral
#This bot will connect to the unofficial Webull API and place trades automatically
from webull import paper_webull, endpoints # for paper trading, import 'paper_webull'
from webull.streamconn import StreamConn
import paho.mqtt.client as mqtt
import json
import trendln
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime
#login to Webull
wb = paper_webull()
f = open("token.txt", "r")
loginInfo = json.load(f)
#print(loginInfo)
if not loginInfo['accessToken']:
    wb.get_mfa('webull email') #mobile number should be okay as well.
    code = input('Enter MFA Code : ')
    loginInfo = wb.login('user', 'pass', 'My Device', code)
    f = open("token.txt", "w")
    f.write(json.dumps(loginInfo))
    f.close()
    print(loginInfo)
else:
    print('Found access token')
    wb.refresh_login()
    loginInfo = wb.login('user', 'pass')
    #print(loginInfo)
def drawChart(hist, update):
    mins, maxs = trendln.calc_support_resistance(hist[-1000:].close)
    minimaIdxs, pmin, mintrend, minwindows = trendln.calc_support_resistance((hist[-1000:].low, None)) #support only
    mins, maxs = trendln.calc_support_resistance((hist[-1000:].low, hist[-1000:].high))
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = mins, maxs
    minimaIdxs, maximaIdxs = trendln.get_extrema(hist[-1000:].close)
    maximaIdxs = trendln.get_extrema((None, hist[-1000:].high)) #maxima only
    minimaIdxs, maximaIdxs = trendln.get_extrema((hist[-1000:].low, hist[-1000:].high))
    fig = trendln.plot_support_resistance(hist[-1000:].close) # requires matplotlib - pip install matplotlib
    #if not update:
    #    plt.savefig('suppres.svg', format='svg')
    #    plt.show()
    #    plt.clf() #clear figure
    fig = trendln.plot_sup_res_date((hist[-1000:].low, hist[-1000:].high), hist[-1000:].index) #requires pandas
    if not update:
        plt.show()
    curdir = '.'
    #if update:
    #    plt.draw()
    #    plt.pause(0.001)
    #trendln.plot_sup_res_learn(curdir, hist)
hist = wb.get_bars(stock='AAPL', interval='m60', count=20, extendTrading=0)
hist = pd.DataFrame(hist)
print(hist)
drawChart(hist, False)
#def on_price_message(topic, data):
#    print (data)
#	#the following fields will vary by topic number you recieve (topic 105 in this case)
#    print(f"Ticker: {topic['tickerId']}, Price: {data['deal']['price']}, "
#        + f"Volume: {data['deal']['volume']}, Trade time: {data['tradeTime']}")
#	#all your algo precessing code goes here

#def on_order_message(topic, data):
#    print(data)
#conn = StreamConn(debug_flg=True)

#conn.price_func = on_price_message
#conn.order_func = on_order_message
#if not loginInfo['accessToken'] is None and len(loginInfo['accessToken']) > 1:
#    conn.connect(wb.did, access_token=wb.access_token)
#else:
#    conn.connect(wb.did)

#conn.subscribe(tId='913256135') #AAPL
#conn.run_loop_once()
#conn.run_blocking_loop() #never returns till script crashes or exits
