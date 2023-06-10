
import streamlit as st

import pandas as pd 
import glob, re
import numpy as np
import datetime

import plotly.graph_objects as go
import plotly.express as px


from plotly.subplots import make_subplots


import pandasql


import platform
import sys

# ADDING PATH FOR SHARED PYTHON CODES
print(sys.path)
print('')
print('Length of sys.path is ', len(sys.path))
print('')

# insert at 1, 0 is the script path (or '' in REPL)
if (platform.node() == 'R2D2') and ('D:\\OneDrive\\Trading\\Shared' not in sys.path):
    sys.path.insert(1, 'D:\\OneDrive\\Trading\\Shared')

if (platform.node() == 'Yoda') and ('C:\\Users\\MasterYoda\\Documents\\OneDrive\\Trading\\Shared' not in sys.path):
    sys.path.insert(1, 'C:\\Users\\MasterYoda\\Documents\\OneDrive\\Trading\\Shared')

print(sys.path)
print('')
print('Length of sys.path is ', len(sys.path))

import funcs

st.set_page_config(layout="wide")

#st.title(' Dashboard ')
#st.header(' This is where the dashboard will be... ')
#st.subheader('...')
st.header('Time in UTC is {}'.format(datetime.datetime.utcnow()))



# SETTING UP THE SIDEBAR
st.sidebar.header('Selections:')
cryptopair = st.sidebar.selectbox('Select a currency pair', ('DOGEUSDT','BTCUSDT'))

st.sidebar.header('Secondary Axis:')
secondary_axis = st.sidebar.selectbox('Select what to plot on secondary y-axis', ('Volume','pct change'))

st.title(cryptopair)

days_behind = st.sidebar.slider('Historical Days to plot', 1 , 25, 20)

time_slice_options = ['1d','8h','4h','2h','1h','30m','15m','5m','1m']
time_slice = st.sidebar.radio("Candlesticks:", time_slice_options) 

st.write('Selected time slice is {}'.format(time_slice))


button_prev = st.sidebar.button('Previous')
button_next = st.sidebar.button('Next')

#st.write(button_prev)
#st.write(button_next)



username = 'elonmusk'

twitter_df = funcs.get_twitter_data(user = username, num_tweets = 200, stringsearch = 'doge')

if time_slice == '1m':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('1min'))
elif time_slice == '5m':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('5min'))
elif time_slice == '15m':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('15min'))
elif time_slice == '30m':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('30min'))
elif time_slice == '1h':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('60min'))
elif time_slice == '2h':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('120min'))
elif time_slice == '4h':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('240min'))
elif time_slice == '8h':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('480min'))
elif time_slice == '1d':
    twitter_df['time_ts_round'] = twitter_df['time'].apply( lambda x: pd.Timestamp(x).floor('D'))

st.write('Twitter df shape is ', twitter_df.shape)

print(twitter_df.columns.values.tolist())

twitter_df = twitter_df.sort_values(by = ['has_strsearch', 'time_ts_round' , 'likes'] , ascending = [False , False, False ]).drop_duplicates(subset = 'time_ts_round', keep="first")
twitter_df = twitter_df[twitter_df.has_strsearch]
twitter_df['tweet'] = twitter_df['tweet'].apply( lambda x : re.sub(r'@\w+', '', x))


twitter_df.to_csv('D:\\GDrive\\Trading\\Tweets\\{username}_tweets.csv', index = False)

st.write('Twitter df shape after removing duplicate round(timestamps) is ', twitter_df.shape)

st.write(twitter_df)    




# FILTERING FOR THE DATES WE NEED THE DATA FOR 
end_tm_utc = datetime.datetime.utcnow()
start_tm_utc = ( end_tm_utc + datetime.timedelta(minutes= -days_behind*24*60) )
print( ' Filtering data from {} to {} '.format( start_tm_utc, end_tm_utc) )
st.write( ' Filtering data from {} to {} '.format( start_tm_utc, end_tm_utc) )



# IMPORTING DATA FOR PLOTTING 
path = "D:\\OneDrive\\Data\\OHLC\\{}\\{}".format(cryptopair, time_slice) # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    datepart_of_filename = filename.split('\\')[-1][ len('klines') + len('_')*4 + len('frm') + len(cryptopair) + len(time_slice) :]
    filename_start_year = int(datepart_of_filename[:4])
    filename_start_month = int(datepart_of_filename[5:7])
    filename_start_date = int(datepart_of_filename[8:10])
    
    filter_start_year = pd.to_datetime(start_tm_utc).year
    filter_start_month = pd.to_datetime(start_tm_utc).month
    filter_start_date = pd.to_datetime(start_tm_utc).day

    if (filename_start_year >= filter_start_year) & (filename_start_month >= filter_start_month)  & (filename_start_date >= filter_start_date):
        df = pd.read_csv(filename, index_col=None, header=0)
        #print(df.shape)
        li.append(df)

alldata = pd.concat(li, axis=0, ignore_index=True)
alldata['timestamp_utc_for_merge'] = alldata['timestamp_utc'].apply( lambda x: pd.Timestamp(x))
st.write('Alldata shape is ', alldata.shape)
#st.write(alldata)

#dogedata = pd.read_csv('D:\\OneDrive\\Trading\\Data\\DOGEUSDT\\30m\\klines_DOGEUSDT_30m_frm_2020_12_27_00_00_00_to_2020_12_27_23_59_59.csv')
#print(alldata.columns.values.tolist())
#print(alldata.shape)


alldata_plus_tweets = alldata.merge(twitter_df, how = 'left', left_on = 'timestamp_utc_for_merge', right_on = 'time_ts_round')
plotdata = alldata_plus_tweets [ ( pd.to_datetime(alldata.timestamp_utc) >= start_tm_utc) & ( pd.to_datetime(alldata.timestamp_utc) <= end_tm_utc) ]

st.write(' Giving us the PLOTDATA whose shape is ', plotdata.shape)






plotdata["pct_change_prev_abs"] = plotdata["pct_change_prev"].abs()

#d = np.average(plotdata.pct_change_prev_abs) * np.average(plotdata.open)
d_frm_candlestick = np.average(plotdata.pct_change_prev_abs) * np.average(plotdata.open)
#d = 0.03
d_tweet = d_frm_candlestick

range_top_vol = max(plotdata.volume)
range_bot_vol = -max(plotdata.volume)
average_vol = np.average(plotdata.volume)

#plotdata["marker"] = np.where( plotdata["open"] < plotdata["close"] , plotdata["high"] + d , plotdata["low"] - d )
plotdata["marker"] = np.where( plotdata["open"] < plotdata["close"] , plotdata["high"] + d_frm_candlestick , plotdata["low"] - d_frm_candlestick )
plotdata["symbol"] = np.where(plotdata["open"] < plotdata["close"], "triangle-up", "triangle-down")
plotdata["color"] = np.where(plotdata["open"] < plotdata["close"], "green", "red")

plotdata["volume_r0"] = plotdata["volume"].round(0)
plotdata["volume_r0_markers"] = plotdata["volume"].round(0) + average_vol*0.25


plotdata["pct_change_color"] = np.where(plotdata["pct_change_prev"] < 0, "red", "green")



plotdata["pct_change_prev"] = plotdata["pct_change_prev"]*100




#plotdata["tweet_marker"] = np.where( plotdata["open"] < plotdata["close"] , plotdata["high"] + d_tweet , plotdata["low"] - d_tweet )
#plotdata["tweet_marker"] = np.where( plotdata["pct_change_prev"] > 0 , plotdata["pct_change_prev"] + d_tweet , plotdata["pct_change_prev"] - d_tweet )


plotdata["tweet_marker"] = plotdata["high"] + 2*d_tweet
#plotdata["tweet_marker"] = plotdata["pct_change_prev_abs"] + d_tweet
#plotdata["tweet_marker"] = plotdata["volume"]
plotdata["tweet_marker_nan"] = np.where(plotdata['has_strsearch'].isnull(), np.nan, plotdata['tweet_marker'])
plotdata["tweet_symbol"] = "star"
plotdata["tweet_color"] = "blue"


plotdata["text_marker"] = plotdata["high"] + d_tweet
plotdata["text_marker_nan"] = plotdata.apply(lambda x : np.nan if np.around(x.pct_change_prev_abs,4)*100 <= 0.08 else x.text_marker, axis =1)

st.write(plotdata)


# PLOTTING THE DATA for reference 

# CODE OPTION A 

#fig = go.Figure()

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace( go.Bar( x = plotdata.timestamp_utc, y = plotdata.volume_r0, opacity=0.20, marker_color='black' , name = 'volume') , secondary_y = True)
#fig.add_trace( go.Bar( x = plotdata.timestamp_utc, y = plotdata.volume_r0, opacity=0.20, marker_color='black' , name = 'volume') )


fig.add_trace( go.Scatter( x = plotdata.timestamp_utc,
                   y = plotdata.tweet_marker_nan,
                   mode='markers',
                   name ='tweet_markers',
                   marker=go.scatter.Marker(size=8, symbol = plotdata.tweet_symbol, color = plotdata.tweet_color) ,
                   hovertemplate = '<b>%{text}</b>',
                   text = plotdata.tweet
                    )
                   )

fig.add_trace(go.Candlestick(x = plotdata.timestamp_utc 
            , open = plotdata.open 
            , close = plotdata.close
            , high = plotdata.high 
            , low = plotdata.low 
            , name = cryptopair)
            )


# if secondary_axis == 'Volume':
#     fig.add_trace( go.Bar( x = plotdata.timestamp_utc, y = plotdata.volume_r0, opacity=0.10, marker_color='black' , name = 'volume') , secondary_y = True)
# elif secondary_axis == 'pct change':
#     fig.add_trace( go.Bar( x = plotdata.timestamp_utc, y = plotdata.pct_change_prev, opacity=0.10, marker_color= plotdata['pct_change_color'] , name = 'pct_change_prev') , secondary_y = True)



fig.add_trace( 
            go.Scatter( x = plotdata.timestamp_utc
            , y = plotdata.text_marker_nan
            , opacity = 0.75
            , mode = 'text'
            , marker_color = plotdata['pct_change_color'] 
            , name = 'pct_change_prev_abs' 
            , text = plotdata['pct_change_prev'].apply(lambda x: '{}%'.format(np.around(x,2) ) )
            #, text = plotdata.pct_change_prev
                )
            #, secondary_y = True
            )




#fig['layout']['yaxis2'].update(range=[range_bot_vol, range_top_vol], autorange=False)



# fig.add_trace(go.Scatter( x = plotdata.timestamp_utc,
#                    y = plotdata.marker,
#                    mode='markers',
#                    name ='markers',
#                    marker=go.scatter.Marker(size=8, symbol = plotdata.symbol, color = plotdata.color))
#             )



#fig.show() gives another tab with chart 

#fig.update_layout( autosize=False, width=800, height=800,)
fig.update_layout(height=1000)
fig.update_layout(showlegend=True) 

#st.write(fig)
st.plotly_chart(fig, use_container_width=True)




# OPTION B ADDING THE BAR CHART
#st.bar_chart(data=plotdata['volume'], use_container_width=True)

#fig2 = go.Figure([go.Bar(x = plotdata.timestamp_utc, y = plotdata.volume)]) 
#st.plotly_chart(fig2, use_container_width=True)

# fig_bar_below_candlestick = px.bar(plotdata, x='timestamp_utc', y='volume',  color='color',  color_discrete_map={'red': 'red', 'green': 'green'})
# fig_bar_below_candlestick.update_layout(width = 1800)
# fig_bar_below_candlestick.update_layout(showlegend=False) 
# st.plotly_chart(fig_bar_below_candlestick, use_container_width=False)


# OPTION C ADDING THE BAR CHART 
# candle_stick = go.Candlestick(x = plotdata.timestamp_utc 
#             , open = plotdata.open 
#             , close = plotdata.close
#             , high = plotdata.high 
#             , low = plotdata.low 
#             , name = option)

# traces = go.Scatter( x = plotdata.timestamp_utc,
#                    y = plotdata.marker,
#                    mode='markers',
#                    name ='markers',
#                    marker=go.scatter.Marker(size=8, symbol = plotdata["symbol"], color = plotdata["color"] ))

# st.plotly_chart( [candle_stick , traces], use_container_width = True)
# OPTION B FINISH



#Other helpful code bit below 
#fig.update_xaxes(type='xaxes')
#st.plotly_chart( [candle_stick], use_container_width = True )
#fig.add_trace( go.Scatter(x = plotdata['timestamp_utc'], y = plotdata['high'] , mode='markers', marker = dict(symbol='triangle-down-open', size = 12) , showlegend = True) )
#st.write(plotdata.shape)

#if option == 'DOGEUSDT (Perpetual)
#fig.show()

st.write(plotdata)




