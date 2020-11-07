#WeBull Trading Bot, by Jacob Amaral
#Youtube : Jacob Amaral
#This bot will connect to the unofficial Webull API and place trades automatically using Support / Resistance on 1 minute candles
from webull import paper_webull, endpoints # for real money trading, just import 'webull' instead
from webull.streamconn import StreamConn
import paho.mqtt.client as mqtt
import json
import trendln
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.interactive(True)
import numpy as np
import pandas as pd
from datetime import datetime
import sched
import time
#Vars
symbol = None
period = None
timeframe = None
hist = []
print("Logging in to WeBull...")
#login to Webull
wb = paper_webull()
f = None
loginInfo = None
try:
    f = open("token.txt", "r")
    loginInfo = json.load(f)
except:
    print("First time login.")
hist = None
support = 0
resistance = 0
enteredTrade = False
s = sched.scheduler(time.time, time.sleep)
#If first time save login as token
if not loginInfo:
    wb.get_mfa('myemail@email.com') #mobile number should be okay as well.
    code = input('Enter MFA Code : ')
    loginInfo = wb.login('myemail@email.com', 'my password', 'My Device', code)
    f = open("token.txt", "w")
    f.write(json.dumps(loginInfo))
    f.close()
else:
    wb.refresh_login()
    loginInfo = wb.login('myemail@email.com', 'my password')
#Draw Chart
def drawChart(hist, update):
    global support
    global resistance
    global symbol
    try :
        mins, maxs = trendln.calc_support_resistance((hist[-1000:].low, hist[-1000:].high))
        support = mins[1][1]
        resistance = maxs[1][1]
        print("Current Support : ", support, " Will buy once " + symbol.upper() + " reaches this number.")
        print("Current Resistance : ", resistance)
        minimaIdxs, maximaIdxs = trendln.get_extrema((hist[-1000:].low, hist[-1000:].high))
        fig = trendln.plot_sup_res_date((hist[-1000:].low, hist[-1000:].high), hist[-1000:].index)
        fig.canvas.set_window_title(symbol.upper() + " Bot")
        fig.suptitle(symbol.upper() + " Support/Resistance Lines")
        plt.draw()
    except Exception as e:
        print('')
#On Bar Update
def run(sc):
    global hist
    global enteredTrade
    global symbol
    global timeframe
    global period
    global s
    hist = pd.DataFrame(hist)
    try:
        #Get current low and high
        low = hist.iloc[len(hist) - 1,2]
        high = hist.iloc[len(hist) - 1,1]
        if(low > 0):
            #Buy at support
            if (low <= support and not enteredTrade):
                order = wb.place_order(stock=symbol.upper(), action='BUY', orderType='MKT', enforce='DAY', quant=1)
                print(order)
                enteredTrade = True
            #Sell at resistance
            if (high >= resistance and enteredTrade):
                order = wb.place_order(stock=symbol.upper(), action='SELL', orderType='MKT', enforce='DAY', quant=1)
                print(order)
                enteredTrade = False
            #Update chart with new data
            hist = wb.get_bars(stock=symbol.upper(), interval='m'+timeframe, count=int((390*int(period))/int(timeframe)), extendTrading=0)
            hist = pd.DataFrame(hist)
            #call this method again every minute for new price changes
            drawChart(hist, True)
    except Exception as e:
        print(str(e))
    s.enter(60, 1, run, (sc,))
    plt.pause(60)
conn = StreamConn(debug_flg=False)
if not loginInfo['accessToken'] is None and len(loginInfo['accessToken']) > 1:
    conn.connect(loginInfo['uuid'], access_token=loginInfo['accessToken'])
else:
    conn.connect(wb.did)
#Initiate our scheduler so we can keep checking every minute for new price changes
s.enter(1, 1, run, (s,))
def get_data():
    global symbol
    global timeframe
    global period
    global hist
    try:
        #Symbol to trade
        symbol = input("Enter the symbol in uppercase letters you want to trade : ")
        print("Streaming real-time data now for " + symbol.upper())
        #Timeframe for candlesticks
        timeframe = input("Enter the timeframe in minutes to trade on (e.g. 1,5,15,60) : ")
        #Period for support / resistance calculation
        period = input("What is the period in days do you want to use to calculate support/resistance (e.g. 1,5,30)  : ")
        #Get enough bars for the period, 390 minutes in 1 trading day multiplied by the period
        hist = wb.get_bars(stock=symbol.upper(), interval='m'+timeframe, count=int((390*int(period))/int(timeframe)), extendTrading=0)
        hist = pd.DataFrame(hist)
        s.run()
    except Exception as e:
        print("Make sure your timeframes are numbers (e.g. 1,5,15). Please try again.")
        get_data()
get_data()
