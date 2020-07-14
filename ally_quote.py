#!/usr/bin/python3

import oauth2 as oauth
import json, simplejson, datetime, threading, os, time, pymongo


curtime1 = datetime.datetime.now()

#print ("Starting" , curtime)

## static id for now

id = 1000

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

CONSUMER_KEY = 'oXVEBpwjzhOd3Pzte880eyvmsdOCLuYnhU7gVLND6Ds0'
CONSUMER_SECRET = '958SCvppRbwiP1G7KmWaG1bHtpQDkM1peP6CP5P8xbw6'
OAUTH_TOKEN = 'i8ZJ0aH2Ne2KgcZ32dUpc50A1xkVjbmlcmlgcKaO0bk2'
OAUTH_SECRET = 'fBIn6qIevvKVEwik5Nn2rwehP7U0gRlUFORQpsRS7pw3'

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
    wk52lo = line['wk52lo']
    wk52hi = line['wk52hi']
    last = line['last']
    insweath = (pair, wk52lo, wk52hi, last)
    curweath.append(insweath)

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
    #print (datax)

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
            curlast = h[3]

            if symbol == curpair:
                if curlow == "na":
                    curlow = bid
                if curhigh == "na":
                    curhigh = ask
                if last == "na":
                    last = bid

                if float(curlow) > float(curhigh):
                    print ("ERROR - ", symbol, " curlow > curhigh -", "bid", bid, "curlow", curlow, "ask", ask, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    weatherins = { "error": "LOW2HI", "pair": curpair, "last": last, "lowest": curlow, "highest": curhigh,  "bid": bid, "ask": ask, "date": datetime.datetime.now() }
                    weatherfix = { "$set": { "last": last, "wk52hi": wk52hi, "wk52lo": wk52lo, "pair": curpair}}

                    weathercol.update_many(pairins, weatherfix)
                    myerrors.insert_one(weatherins)

                if float(curhigh) < float(curlow):
                    print ("ERROR - ", symbol, " curhigh < curlow -", "bid", bid, "curlow", curlow, "ask", ask, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    weatherins = { "error": "HI2LOW", "pair": curpair, "last": last, "lowest": curlow, "highest": curhigh,  "bid": bid, "ask": ask, "date": datetime.datetime.now() }
                    weatherfix = { "$set": { "last": last, "wk52hi": wk52hi, "wk52lo": wk52lo, "pair": curpair}}

                    weathercol.update_many(pairins, weatherfix)
                    myerrors.insert_one(weatherins)

                #if bid < curlow:
                if float(last) < float(curlow):
                    print ("LOW", symbol, "bid", bid, "curlow", curlow, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    
                    weatherlow = { "$set": { "last": last, "wk52hi": wk52hi, "wk52lo": last, "pair": curpair}}
                    weatherlowins = { "cond": "low", "last": last, "highest": curhigh, "date": datetime.datetime.now(), "lowest": ask, "percentchange": pchg, "pair": curpair, "bid": bid, "ask": ask }
                    weathercol.update_many(pairins, weatherlow)
                    myalert.insert_one(weatherlowins)

                #if ask > curhigh:
                if float(last) > float(curhigh):
                    print ("HIGH", symbol, "ask", ask, "curlow", curlow, "curhigh", curhigh, "last", last)
                    pairins = { "pair": symbol }
                    weatherhi = { "$set": { "last": last, "wk52hi": last, "wk52lo": wk52lo, "pair": curpair}}
                    weatherhiins = { "cond": "high", "pair": curpair, "last": last, "percentchange": pchg, "low": curlow, "high": bid, "date": datetime.datetime.now(), "bid": bid, "ask": ask }
                    weathercol.update_many(pairins, weatherhi)
                    myalert.insert_one(weatherhiins)
                else:
                    pairins = { "pair": symbol }

                    weatherins = { "$set": { "last": last, "wk52hi": wk52hi, "wk52lo": wk52lo, "pair": curpair}}
                    weathercol.update_many(pairins, weatherins)

curtime2 = datetime.datetime.now()
print ("Started ", curtime1)
print ("Ended ", curtime2)


