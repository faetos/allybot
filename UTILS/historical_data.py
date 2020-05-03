#!/usr/bin/python3

import urllib, simplejson, threading, pymongo, datetime, os, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError

### DB stuffs

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ally"]
mycol = mydb["price"]
mypairs = mydb["pairs"]
weathercol = mydb["weather"]

###time

curtime = datetime.datetime.now()

list1 = []

#list1 = 'TMRC, MSFT, AACG, AAL, AAME'
for v in mypairs.find():
    pair = v['pair']
    list1.append(pair)

#rlist = open("small_list", "r")


url = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol="
apikey = "&apikey=YOUR_API_KEY"

ctr = 0
dayctr = 0
daynum = 490
itr = 0
minnum = 5
daysleep = 86700

for x in list1:
#for x in list1:
    print ("Next up:", x)
    already = weathercol.count_documents({ "pair": x }, limit = 1)
    if already == True:
        print (x, "is already in there - skipping")
    if ctr < minnum and dayctr < daynum and already == False:
        ctr += 1
        dayctr += 1
        request = Request(url + x + apikey)
    #request = Request(url)

        response = urlopen(request)
        #raw = simplejson.load(response)
        #print ("RESPONSE: ", raw)
        stuff = simplejson.load(response)['Monthly Time Series']

        lows = []
        his = []

        keys = (stuff.keys())
        for key in keys:
            #print(key)
            hi = stuff[key]['2. high']
            lo = stuff[key]['3. low']
            lows.append(lo)
            his.append(hi)

### grab the data look for low and high and sort by highest and lowest numbers and save those 2 values with the ticker symbol
    #print (stuff)

        lowest = min(lows)
        highest = max(his)
    
        print (x)
        print ("Lowest", lowest)
        print ("Highest", highest)

        datains = { "pair": x, "lowest": lowest, "highest": highest }
        weathercol.insert_one(datains)

        #time.sleep(1)
   
    if ctr == minnum and dayctr < daynum and already == False:
        print ("Minute up - sleeping 70 seconds")
        time.sleep(70)
        ctr = 0
        ctr += 1
        dayctr += 1
        request = Request(url + x + apikey)
    #request = Request(url)

        response = urlopen(request)
        #raw = simplejson.load(response)
        #print ("RESPONSE: ", raw)
        stuff = simplejson.load(response)['Monthly Time Series']

        lows = []
        his = []

        keys = (stuff.keys())
        for key in keys:
            #print(key)
            hi = stuff[key]['2. high']
            lo = stuff[key]['3. low']
            lows.append(lo)
            his.append(hi)

### grab the data look for low and high and sort by highest and lowest numbers and save those 2 values with the ticker symbol
    #print (stuff)

        lowest = min(lows)
        highest = max(his)

        print (x)
        print ("Lowest", lowest)
        print ("Highest", highest)
        datains = { "pair": x, "lowest": lowest, "highest": highest }
        weathercol.insert_one(datains)

        time.sleep(1)

    if dayctr == daynum and already == False:
        print ("done for the day - sleeping until tomorrow") 
        #time.sleep(86700)
        time.sleep(70)
        ctr = 0
        dayctr = 0

        request = Request(url + x + apikey)
    #request = Request(url)

        response = urlopen(request)
        #raw = simplejson.load(response)
        #print ("RESPONSE: ", raw)
        stuff = simplejson.load(response)['Monthly Time Series']

        lows = []
        his = []

        keys = (stuff.keys())
        for key in keys:
            #print(key)
            hi = stuff[key]['2. high']
            lo = stuff[key]['3. low']
            lows.append(lo)
            his.append(hi)

### grab the data look for low and high and sort by highest and lowest numbers and save those 2 values with the ticker symbol
    #print (stuff)

        lowest = min(lows)
        highest = max(his)

        print (x)
        print ("Lowest", lowest)
        print ("Highest", highest)

        datains = { "pair": x, "lowest": lowest, "highest": highest }
        weathercol.insert_one(datains)

        time.sleep(1)
