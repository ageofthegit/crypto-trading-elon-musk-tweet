

import streamlit as st

import pandas as pd 
import glob
import numpy as np
import datetime

import plotly.graph_objects as go


st.set_page_config(layout="wide")

#st.title(' Dashboard ')
#st.header(' This is where the dashboard will be... ')
#st.subheader('...')
st.header('Time in UTC is {}'.format(datetime.datetime.utcnow()))



# SETTING UP THE SIDEBAR
st.sidebar.header('Selections:')

option = st.sidebar.selectbox('Select a currency pair', ('DOGEUSDT (Perpetual)','BTCUSDT (Perpetual)'))

st.title(option)

days_behind = st.sidebar.slider('Historical Days to plot', 1 , 10, 2)

button_prev = st.sidebar.button('Previous')
button_next = st.sidebar.button('Next')

#st.write(button_prev)
#st.write(button_next)


# IMPORTING DATA FOR PLOTTING 
path = "D:\\OneDrive\\Trading\\Data\\DOGEUSDT\\30m" # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

alldata = pd.concat(li, axis=0, ignore_index=True)
#dogedata = pd.read_csv('D:\\OneDrive\\Trading\\Data\\DOGEUSDT\\30m\\klines_DOGEUSDT_30m_frm_2020_12_27_00_00_00_to_2020_12_27_23_59_59.csv')
print(alldata.columns.values.tolist())


end_tm_utc = datetime.datetime.utcnow()
start_tm_utc = ( end_tm_utc + datetime.timedelta(minutes= -days_behind*24*60) )


plotdata = alldata [ ( pd.to_datetime(alldata.timestamp_utc) >= start_tm_utc) & ( pd.to_datetime(alldata.timestamp_utc) <= end_tm_utc) ]


# PLOTTING THE DATA fro reference 
fig = go.Figure(data = [ go.Candlestick(x = plotdata['timestamp_utc'] , open = plotdata['open'] , close = plotdata['close'], high = plotdata['high'] , low = plotdata['low'] , name = option ) ])
#fig.update_xaxes(type='xaxes')
fig.update_layout(height=1000)
st.plotly_chart(fig, use_container_width = True )


#fig.add_trace( go.Scatter(x = plotdata['timestamp_utc'], y = plotdata['high'] , mode='markers', marker = dict(symbol='triangle-down-open', size = 12) , showlegend = True) )
go.Scatter(x = plotdata['timestamp_utc'], y = plotdata['high'] , mode='markers', marker = dict(symbol='triangle-down-open', size = 12) , showlegend = True)

#st.write(plotdata.shape)

#if option == 'DOGEUSDT (Perpetual)
#fig.show()

st.write(plotdata)

