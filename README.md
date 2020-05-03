# allybot
Ally.com stock trading bot

Currently under development 

Currently uses a local mongodb as data storage. 

Modules:

 - balance - will pull current balance data for the associated API key
 - holdings - pulls all the current stock holdings for the user
 - quote - pulls a list of quotes (100 at a time - current limit) for the entire stock.list
 
TEST - current developmnent

 - alert - current testing of comparing historical lows/highs against current price
 - weather - basic scoring mechanism to determine risk ratios

UTIL - utilities

 - historical - pulls lows/highs from www.alphavantage.co - timeboxed - 5 calls a minute - requires an API key

Todo 

 - buy/sell - automatically buy or sell
 - reports - report mechanism
 - api - callable via api
 - weather/alerts - scoring mechanisms, ability to write algos within the code and test
