import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

st.set_page_config(layout = "wide")
total = pd.read_pickle('../data/sim.pkl')
total['year'] = total.date_from.dt.year
diff = total[total['different']]

pd.options.plotting.backend = 'plotly'

plot1 = pd.crosstab(total.year, total.keyword, margins=True)
plot1 = plot1.drop(['All'], axis=0)
plot2 = pd.crosstab(diff.year, diff.keyword, margins=True)
plot2 = plot2.drop(['All'], axis=0)

plot = plot2.div(plot1['All'], axis=0).fillna(0)
# plot

st.title('PoliVis')

# Only a subset of options make sense
x_options = plot.columns

# Allow use to choose
x_axis = st.multiselect('Which issue do you want to explore?', x_options,['North Korea'])
# # plot the value
# fig = px.scatter(df,
#                 x=x_axis,
#                 y='rating',
#                 hover_name='name',
#                 title=f'Cereal ratings vs. {x_axis}')
data = plot[x_axis]
fig = data.plot()
selected_points = plotly_events(fig)