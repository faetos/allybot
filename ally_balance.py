#!/usr/bin/python3

import oauth2 as oauth
import simplejson, threading, json, pymongo, time

##api.tradeking.com loging info

CONSUMER_KEY = 'x'
CONSUMER_SECRET = 'y'
OAUTH_TOKEN = 'z'
OAUTH_SECRET = 't'

## static id for now

id = 1

### DB stuffs - truncate table and replace it with new data

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ally"]
mybal = mydb["bal"]


### end DB stuffs


## api url to get balabce info - includes client ID - need to replace at some point

apiurl = "https://api.tradeking.com/v1/accounts/YOURACCTNUM/balances.json"

oAuthConsumer = oauth.Consumer(
    CONSUMER_KEY,
    CONSUMER_SECRET)

oAuthToken = oauth.Token(
    OAUTH_TOKEN,
    OAUTH_SECRET)

oAuthRequest = oauth.Client(oAuthConsumer, oAuthToken)

response, content = oAuthRequest.request(apiurl)

data = simplejson.loads(content)

for x in data:
    acctval = data[x]['accountbalance']['accountvalue']
    cash = data[x]['accountbalance']['money']['cash']
    unset = data[x]['accountbalance']['money']['unsettledfunds']
    stocks = data[x]['accountbalance']['securities']['total']
    play = data[x]['accountbalance']['money']['cashavailable']
    unsettledfunds = data[x]['accountbalance']['money']['unsettledfunds']

    idins = { "id": id }
    #datains = { "id": id, "acctval": acctval, "cash": cash, "unset": unset, "stocks": stocks, "play": play, "unset": unsettledfunds }
    datains = { "$set": { "id": id, "acctval": acctval, "cash": cash, "unset": unset, "stocks": stocks, "play": play, "unset": unsettledfunds }}
    #mybal.insert_one(datains)
    mybal.update_many(idins, datains)


    #print ("account value", acctval)
    #print ("stocks", stocks)
    #print ("cash", play)
    #print ("unsettled funds", unsettledfunds)

    #print ("total invested", acctval)
    #print ("total avail to buy", play)

