#!/usr/bin/python3

import pymongo,datetime
#from twilio.rest import TwilioRestClient

### DB stuffs

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ally"]
myalert = mydb["alert"]
allypairs = mydb["pairs"]
allyprice = mydb["price"]
weather = mydb["weather"]
allyweatherhist = mydb["weatherhist"]
allyhold = mydb["holdings"]
ignore = mydb["ignore"]
watch = mydb["watch"]


#sort for latest document
#cursor = mongo.db.measurements.find().sort([('timestamp', -1)]).limit(1)

# datetime

cur_time = datetime.datetime.now()
        
alerts = []
pairlisto = []
lowalerts = []
highalerts = []
lastalert = []
holdings = []
ignorelist = []
watchlist = []

### find list of stocks and make it unique

for x in myalert.find():
    pair = x['pair']
    pairlisto.append(pair)

### get list of what user already holds

for x in allyhold.find():
    pair = x['sym']
    holdings.append(pair)

### grab stocks to ignore

for x in ignore.find():
    pair = x['pair']
    ignorelist.append(pair)

### grab watch list

for x in watch.find():
    pair = x['pair']
    watchlist.append(pair)

#for s in holdings:
#    own = s[0]

## make sure list is unique
pairlist = sorted(set(pairlisto))
#print (pairlist)

### find the count of times it is in the DB
for y in pairlist:

    findlowcount = { "cond": "low", "pair": y }
    count = myalert.find(findlowcount).count()
    lows = (y, count)
    #lowalerts.append(lows)
    #print ("low", y, count)

    findhighcount = { "cond": "high", "pair": y }
    count = myalert.find(findhighcount).count()
    highs = (y, count)
    #highalerts.append(highs)
    #print ("high", y, count)

### find the alerts and add them to a list

    lastfind = myalert.find({ "pair": y }).sort( "date", -1 ).limit(1)
    for j in lastfind:
        pair = j['pair']
        #print (pair)
        cond = j['cond']
        last = j['last']
        #low = j['lowest']
        #high = j['highest']
        date = j['date']
        pct = j['percentchange']
        score = j['score']
        alertins = (pair, cond, last, date, pct, score, count)
        #print (alertins)
        alerts.append(alertins)

#{ "_id" : ObjectId("5e99d293c655dc7382e7d941"), "cond" : "low", "last" : "11.795", "highest" : "46.9600", "date" : ISODate("2020-04-17T16:00:19.326Z"), "score" : "0", "lowest" : "11.795", "percentchange" : "5.78", "pair" : "ALEX" }

### find the latest alert and action on it

for p in alerts:
    curpair = p[0]
    cond = p[1]
    last = p[2]
    pct = p[4]
    score = p[5]
    count = p[6]
    if count >= 1:
    #if count >= 1 and count <= 5:
        if cond == "low" and curpair not in holdings and curpair not in ignorelist and curpair not in watchlist and float(last) >= 10:
            print ("ALERT: BUY", curpair, "percent", pct, "last", last, "score", score, "count", count)
        if cond == "low" and curpair not in holdings and curpair not in ignorelist and curpair not in watchlist and float(last) < 10:
            print ("CHEAP: BUY", curpair, "percent", pct, "last", last, "score", score, "count", count)
    #if count > 5:
        #if cond == "high":
        #    print ("ALERT: SELL", curpair, "percent", pct, "last", last, "score", score, "count", count)
        if cond == "low" and curpair in holdings:
            print ("OWN already not buying", curpair, "percent", pct, "last", last, "score", score, "count", count)
        if cond == "high" and curpair in holdings:
            print ("OWN need to: SELL", curpair, "percent", pct, "last", last, "score", score, "count", count)


