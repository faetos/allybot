#!/usr/bin/python3

import oauth2 as oauth
import simplejson, threading, json, pymongo

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
myhold = mydb["holdings"]


### end DB stuffs

myhold.drop()


## api url to get holdings info - includes client ID - need to replace at some point

apiurl = "https://api.tradeking.com/v1/accounts/YOURACCTNUM/holdings.json"

oAuthConsumer = oauth.Consumer(
    CONSUMER_KEY,
    CONSUMER_SECRET)

oAuthToken = oauth.Token(
    OAUTH_TOKEN,
    OAUTH_SECRET)

oAuthRequest = oauth.Client(oAuthConsumer, oAuthToken)

response, content = oAuthRequest.request(apiurl)


data = simplejson.loads(content)['response']['accountholdings']['holding']


holdings = []

for x in data:
    
    sym = x['instrument']['sym']
    price = x['price']
    qty = x['qty']
    gl = x['gainloss']

    palist = (sym, price, qty, gl)
    holdings.append(palist)

myhold.drop()

for y in holdings:

    sym = y[0]
    price = y[1]
    qty = y[2]
    gl = y[3]

    holdlist = { "id": id, "sym": sym, "price": price, "qty": qty, "gl": gl }
    myhold.insert_one(holdlist)
