#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install tweepy


# In[2]:


'''
PURPOSE : THIS CODE AUTOMATES THE BUY OF DOGE WITHIN 15s span of Elon Musk Tweeting
'''

# Variable for binance buy 
symbol_buy = 'DOGEUSDT'
margintype_arg = 'ISOLATED' 
leverage_arg = 10
call_back_rate_arg = 1.0
percentage_buy = 1.00

precision = 'NA'
step_size = 'NA'


# Variable for tweet collection  

number_of_tweets = 1
stringsearch = 'doge'
enter_the_dragon = True
userid = 'elonmusk'
#userid = 'MoMorMorpheus'

# Wait between tweet collection & amongst other parts of the code 
wait_in_seconds = 15

# To handle tweepy connection issues
tweet_missed = 0
tweet_found = 0


# # FUTURES.PY 

# ## WHICH COMPUTER?  

# In[3]:


import platform

'''
if platform.node() = 'Yoda':
    print('Remote server')
if platform.node() = 'R2D2':
    print('My own computer')

'''


# ## ADDING THE SHARED FOLDER TO SYS.PATH FOR IMPORTING SHARED FILES  

# In[4]:



import sys

print(sys.path)
print('')
print('Length of sys.path is ', len(sys.path))
print('')

# insert at 1, 0 is the script path (or '' in REPL)
if (platform.node() == 'R2D2') and ('D:\\GDrive\\Trading\\Shared' not in sys.path):
    sys.path.insert(1, 'D:\\GDrive\\Trading\\Shared')
    
if (platform.node() == 'wormhole') and ('C:\\Users\\frappucino\\Google Drive\\Trading\\Shared' not in sys.path):
    sys.path.insert(1, 'C:\\Users\\frappucino\\Google Drive\\Trading\\Shared')

print(sys.path)
print('')
print('Length of sys.path is ', len(sys.path))


# ### IMPORTING SHARED FILES

# In[5]:



import shared
#import funcs
import twitter


# ### IMPORTING OTHER MODULES

# In[6]:



import datetime
import pandas as pd
import pytz, pprint
import pprint 
import math

# In[7]:


# for creating folders 
import os


# for looping
import time


# In[8]:


# for logging

import logging 
from datetime import date


# In[9]:


# for twittermining
import tweepy
import re

print('Start time is ', datetime.datetime.now())

# ### DEFINIING THE LOGFILE ATTRIBUTES

# In[10]:



# setting logger level for output

# insert at 1, 0 is the script path (or '' in REPL)

logfilename = 'Automated_TwitterMining_{}_{}.log'.format(date.today().strftime("%Y_%m_%d"), userid)

if (platform.node() == 'R2D2'):
    logging.basicConfig(handlers= [logging.FileHandler( '{}\\Logs\\{}'.format( shared.shared_path_r2d2,logfilename), 'w', 'utf-8')]
                        # filename = 'D:\\OneDrive\\Trading\\Logs\\{}'.format(logfilename)
                        , level = logging.DEBUG
                        , force = True
                        , format = '%(asctime)s:\t%(message)s'
                        , datefmt ='%Y-%m-%d %H:%M')
    
if (platform.node() == 'wormhole'):
    logging.basicConfig(handlers= [logging.FileHandler( '{}\\Logs\\{}'.format( shared.shared_path_wormhole, logfilename), 'w', 'utf-8')]
                        #, filename='C:\\Users\\MasterYoda\\Documents\\OneDrive\\Trading\\Logs\\{}'.format(logfilename)
                        , level=logging.DEBUG
                        , force =True
                        , format='%(asctime)s:\t%(message)s'
                        , datefmt='%Y-%m-%d %H:%M')


# In[11]:



logger = logging.getLogger()

#logger.setLevel(level= logging.DEBUG) 
logger.setLevel(level= logging.INFO) 

print('Logger defined at {}'.format(datetime.datetime.now()))
logging.info('Logger defined')

# In[12]:



# Twitter analysis 

auth = tweepy.OAuthHandler(twitter.consumer_key, twitter.consumer_secret)
auth.set_access_token(twitter.access_token, twitter.access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

print('Twitter auth at {}'.format(datetime.datetime.now()))
logging.info('Twitter auth')



# 
# ### UPDATE BINANCE METRICS a) which symbol to buy b) margintype c) leverage 
# 

# In[13]:




# CHANGING MARGIN HERE
try:
    success = shared.client_future.futures_change_margin_type(symbol = symbol_buy, marginType = margintype_arg)
    if success['msg'] == 'success':
        logging.info('Margin changed to \'{}\' '.format(margintype_arg))
except:
    logging.info('Margin is \'{}\' , already'.format(margintype_arg))

# CHANGING LEVERAGE HERE
try:
    shared.client_future.futures_change_leverage(symbol = symbol_buy, leverage = leverage_arg)
    logging.info('Leverage changed to {}'.format(leverage_arg))
except:
    logging.info('Change leverage from \'{}\', did not work'.format(leverage_arg))

print('Binance mets updated at {}'.format(datetime.datetime.now()))
logging.info('Binance mets updated')

time.sleep(60)

# ### d) percentage_buy for quantity

# In[ ]:




# You ask for the balance
future_account_balance = shared.client_future.futures_account_balance()
#print(future_account_balance)

for bal_loop_var in future_account_balance:
    if bal_loop_var['asset']=='USDT':
        balance = float(bal_loop_var['balance'])
        balance_usable = float(bal_loop_var['withdrawAvailable'])

#print(type(balance))
#print(balance)

# set the percentage or fraction you want to invest in each order
portion_balance = balance_usable*percentage_buy

#print(type(portion_balance))
#print(portion_balance)

# based on precision get the quantity you can buy 
step_size = 0

'''

# MANUALLY INSERTING PRECISION 

for f in symbol_info['filters']:
    if f['filterType'] == 'LOT_SIZE':
        step_size = float(f['stepSize'])
        print(step_size)

precision = int(round(-math.log(step_size, 10), 0))
'''
precision = 0

price = float(shared.client_future.futures_symbol_ticker(symbol = symbol_buy)['price'])

quantity_buy = portion_balance / price
#print(quantity_buy)
#quantity_buy = float(round(quantity_buy, precision))
quantity_buy = math.floor(quantity_buy)
#print(type(quantity_buy))
#print(quantity_buy)

print('With balance:{}, percentage_buy:{}, portion_balance:{}, price:{}, quantity_buy:{}, precision:{}, step_size:{}'.format(balance_usable, percentage_buy, portion_balance, price, quantity_buy, precision, step_size))
logging.info('With balance:{}, percentage_buy:{}, portion_balance:{}, price:{}, quantity_buy:{}, precision:{}, step_size:{}'.format(balance_usable, percentage_buy, portion_balance, price, quantity_buy, precision, step_size))

print('Buy quantity updated at {}'.format(datetime.datetime.now()))
logging.info('Buy quantity updated at')


# ### TWITTER ALGO

# In[14]:




# GET FIRST TWEET
tweets_df = pd.DataFrame(columns = ['time','tweet','reply_to','likes','source', 'has_strsearch'])



#for i in tweepy.Cursor(api.user_timeline , id = 'elonmusk', tweetmode = "extended", exclude_replies = False , include_rts = True).items(number_of_tweets):
for i in tweepy.Cursor(api.user_timeline , id = userid, tweetmode = "extended", exclude_replies = False , include_rts = True).items(number_of_tweets):
    #print('\tLast tweet is \'{}\''.format(i.text))
    logging.info('\tLast tweet is \'{}\''.format(i.text))
    last_tweet = i.text
    last_tweet_clean = re.sub(r'@\w+', '', i.text)
    print(last_tweet_clean)
    tweets_df.loc[len(tweets_df)] = [i.created_at, last_tweet_clean, i.in_reply_to_screen_name, i.favorite_count, i.source,  bool(re.search(stringsearch, last_tweet_clean , re.IGNORECASE)) ]
    print(datetime.datetime.now())

print('First tweet found at {} and is {}'.format(datetime.datetime.now(), last_tweet ) )
logging.info('First tweet defined is {}'.format(last_tweet_clean))




# WHILE LAST TWEET DOES NOT CONTAIN DOGE, RUN LOOP
while (enter_the_dragon):
    #print('')
    logging.info('')
    this_tweets_df = pd.DataFrame(columns = ['time','tweet','reply_to','likes','source', 'has_strsearch'])
    
        
    
    # IF Tweepy causes error then wait for another 20 minutes and then run
    while True:
        try:
            tweets = tweepy.Cursor(api.user_timeline , id = userid, tweetmode = "extended", exclude_replies = False , include_rts = True).items(number_of_tweets)
            print(tweets)
            logging.info(tweets)
        except tweepy.TweepError:
            print('Tweepy Error, waiting another 120 seconds and trying again')
            logging.debug('Tweepy Error, waiting another 120 seconds and trying again')
            time.sleep(120) # sleep for 2 minutes
            continue
        else:
            break

    #for i in tweepy.Cursor(api.user_timeline , id = 'elonmusk', tweetmode = "extended", exclude_replies = False , include_rts = True).items(number_of_tweets):
    #for i in tweepy.Cursor(api.user_timeline , id = userid, tweetmode = "extended", exclude_replies = False , include_rts = True).items(number_of_tweets):
    
    for i in tweets:        
        print('Inserting row at {}'.format(len(this_tweets_df)))
        logging.info('Inserting row at {}'.format(len(this_tweets_df)))
        
        this_tweet = i.text
        print('Value of tweet from cursor is {} '.format(i.text))
        logging.info('Value of tweet from cursor is {} '.format(i.text))
        
        this_tweet_clean = re.sub(r'@\w+', '', i.text)        
        this_tweets_df.loc[len(this_tweets_df)] = [i.created_at, this_tweet_clean, i.in_reply_to_screen_name, i.favorite_count, i.source,  bool(re.search(stringsearch, this_tweet_clean , re.IGNORECASE))]
        
        print('Tweet from this_tweets_df is {}'.format(this_tweets_df.tweet.tolist()))
        logging.info('Tweet form this_tweets_df is {} '.format(this_tweets_df.tweet.tolist()))

        logging.info('Buy Binance loop will run based on \'doge\' search: {}'.format(this_tweets_df.has_strsearch.tolist()))
        print('Buy Binance loop will run based \'doge\' search: {}'.format(this_tweets_df.has_strsearch.tolist()))
                
        print(this_tweets_df.shape)
        logging.info(this_tweets_df.shape)
                
        
    if not this_tweets_df.empty:
        print('this_tweets_df has been created and is not empty')
        logging.info('this_tweets_df has been created and is not empty')
        tweet_found = tweet_found + 1
        
        if (this_tweets_df.has_strsearch.tolist()[0]) & (this_tweet != last_tweet):

            logging.info('\tExecute buy doge order on binance')
            print('\tExecute buy doge order on binance')
            #orderdetails = shared.client_future.futures_create_order(symbol=symbol_buy, side='BUY', type='MARKET', quantity = quantity_buy)
            order_details = shared.client_future.futures_create_order(symbol = symbol_buy
                                                                    , side=shared.client_future.SIDE_BUY
                                                                    , type = shared.client_future.ORDER_TYPE_MARKET
                                                                    , quantity = quantity_buy)

            for orders in shared.client_future.futures_account_trades()[-10:]:
                if orders['orderId'] == order_details['orderId']:
                    price_bought_at = orders['price']
                    qty_bought_at = orders['qty']
                    orderdetails_sell_trailing_stop = shared.client_future.futures_create_order(symbol = symbol_buy
                                                                                                , type = "TRAILING_STOP_MARKET"
                                                                                                , callbackRate = call_back_rate_arg
                                                                                                , side = shared.client_future.SIDE_SELL
                                                                                                , quantity= qty_bought_at
                                                                                                , reduceOnly = False
                                                                                                , activatePrice = price_bought_at )

            enter_the_dragon = False

            #print('\tExit')
            logging.info('\tExit')
            break
        else:
            #print('\tNo doge found in THIS tweet, wait for another {} seconds '.format(wait_in_seconds))
            last_tweet = this_tweet
            logging.info('\tNo doge found in THIS tweet, wait for another {} seconds and swap the value of this tweet and last tweet'.format(wait_in_seconds))

    else:
        print('This_tweets_df NOT created, check code after run. It will continue for now after wait time of {} seconds...'.format(wait_in_seconds))
        logging.info('This_tweets_df NOT created, check code after run. It will continue for now after wait time of {} seconds...'.format(wait_in_seconds))
        tweet_missed = tweet_missed + 1
        
    del this_tweets_df
    print('tweet_missed:{}, tweet_found:{}'.format(tweet_missed, tweet_found))
    logging.info('tweet_missed:{}, tweet_found:{}'.format(tweet_missed, tweet_found))
    print('')

    time.sleep(wait_in_seconds)
    #logging.info(datetime.datetime.now())

# In[ ]:




