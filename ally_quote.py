#!/usr/bin/python3

import oauth2 as oauth
import json, simplejson, datetime, threading, os, time, pymongo


curtime = datetime.datetime.now()

#print ("Starting" , curtime)

## static id for now

id = 1

### DB stuffs - truncate table and replace it with new data

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ally"]
myplist = mydb["plist"]
mypairs = mydb["pairs"]
weathercol = mydb["weather"]
myprice = mydb["price"]
myalert = mydb["alert"]
myerrors = mydb["errors"]

### end DB stuffs

### auth

CONSUMER_KEY = 'x'
CONSUMER_SECRET = 'y'
OAUTH_TOKEN = 'z'
OAUTH_SECRET = 't'

apiurl = "https://api.tradeking.com/v1/market/ext/quotes.json?symbols="

oAuthConsumer = oauth.Consumer(
    CONSUMER_KEY,
    CONSUMER_SECRET)

oAuthToken = oauth.Token(
    OAUTH_TOKEN,
    OAUTH_SECRET)

### Current weather - will modify if the high or low is more or less than the current values

curweath = []
getweather = weathercol.find()
for line in getweather:
    #print (line)
    pair = line['pair']
    lowest = line['lowest']
    highest = line['highest']
#    date = line['date']
    scorex = line['score']
    last = line['last']
    pct = line['percentchange']
    insweath = (pair, lowest, highest, scorex, last, pct)
#    insweath = (pair, lowest, highest)
    curweath.append(insweath)

#apilist = []

for h in curweath:
    curpair = h[0]
    curlow = h[1]
    curhigh = h[2]
    #curdate = h[3]
    curscore = h[3]
    curlast = h[4]
    curpct = h[5]

### List of stock symbols

apilist = []

for x in myplist.find():
    pnuts = x['pairs']
    apilist.append(pnuts)


myprice.drop()

for u in apilist:

    time.sleep(2)

    oAuthRequest = oauth.Client(oAuthConsumer, oAuthToken)
    response, content = oAuthRequest.request(apiurl+u)
    datax = simplejson.loads(content)['response']['quotes']['quote']

    for x in datax:
        bid = x['bid']
        ask = x['ask']
        symbol = x['symbol']
        yeild = x['yield']
        pchg = x['pchg']
        prchg = x['prchg']
        wk52lo = x['wk52lo']
        vl = x['vl']
        volatility12 = x['volatility12']
        beta = x['beta']
        wk52hi = x['wk52hi']
        last = x['last']

        ## need to remove non-alphanumeric characters like \' \[ \] in symbol

        for ch in ["[","'"," ","\\n","]"]:
            if ch in symbol:
                symbol = symbol.replace(ch,"")
        
        priceins = { "pair": symbol, "bid": bid, "ask": ask, "yeild": yeild, "pchg": pchg, "prchg": prchg, "wk52lo": wk52lo, "vl": vl, "volat": volatility12, "beta": beta, "wk52hi": wk52hi, "last": last }
        myprice.insert_one(priceins)

        for h in curweath:
            #print (h)
            curpair = h[0]
            curlow = h[1]
            curhigh = h[2]
            #curdate = h[3]
            curscore = h[3]
            curlast = h[4]
            curpct = h[5]

            if symbol == curpair:

                if float(curlow) > float(curhigh):
                    #print ("ERROR - ", symbol, " curlow > curhigh -", "bid", bid, "curlow", curlow, "ask", ask, "curhigh", curhigh, "last", last)
                    weatherins = { "error": "LOW2HI", "pair": curpair, "last": last, "lowest": curlow, "highest": curhigh,  "bid": bid, "ask": ask, "date": datetime.datetime.now() }
                    myerrors.insert_one(weatherins)

                if float(curhigh) < float(curlow):
                    #print ("ERROR - ", symbol, " curhigh < curlow -", "bid", bid, "curlow", curlow, "ask", ask, "curhigh", curhigh, "last", last)
                    weatherins = { "error": "HI2LOW", "pair": curpair, "last": last, "lowest": curlow, "highest": curhigh,  "bid": bid, "ask": ask, "date": datetime.datetime.now() }
                    myerrors.insert_one(weatherins)

                #if bid < curlow:
                if float(ask) < float(curlow):
                    #print ("LOW", symbol, "bid", bid, "curlow", curlow, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    ### disdis - need to add lines to weather with some bogusscores
                    weatherlow = { "$set": { "last": last, "highest": curhigh, "date": datetime.datetime.now(), "score": curscore, "lowest": ask, "percentchange": pchg, "pair": curpair, "bid": bid, "ask": ask }}
                    weatherlowins = { "cond": "low", "last": last, "highest": curhigh, "date": datetime.datetime.now(), "score": curscore, "lowest": ask, "percentchange": pchg, "pair": curpair, "bid": bid, "ask": ask }
                    weathercol.update_many(pairins, weatherlow)
                    myalert.insert_one(weatherlowins)

                #if ask > curhigh:
                if float(bid) > float(curhigh):
                    #print ("HIGH", symbol, "ask", ask, "curlow", curlow, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    weatherhi = { "$set": { "pair": curpair, "last": last, "percentchange": pchg, "lowest": curlow, "highest": bid, "score": curscore, "date": datetime.datetime.now(), "bid": bid, "ask": ask }}
                    weatherhiins = { "cond": "high", "pair": curpair, "last": last, "percentchange": pchg, "low": curlow, "high": bid, "score": curscore, "date": datetime.datetime.now(), "bid": bid, "ask": ask }
                    weathercol.update_many(pairins, weatherhi)
                    myalert.insert_one(weatherhiins)
                else:
                    pairins = { "pair": symbol }
                    weatherins = { "$set": { "pair": curpair, "last": last, "percentchange": pchg, "lowest": curlow, "highest": curhigh, "score": curscore, "date": datetime.datetime.now(), "bid": bid, "ask": ask }}
                    #weatherins = { "$set": { "pair": curpair, "last": last, "percentchange": "0", "lowest": curlow, "highest": curhigh, "score": "0", "date": datetime.datetime.now() }}
                    weathercol.update_many(pairins, weatherins)

curtime = datetime.datetime.now()

#print ("Ended ", curtime)


