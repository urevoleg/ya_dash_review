import datetime as dt
import random

from dateutil.parser import parse

from dash import Dash, html, dcc, callback, Output, Input
import dash_datetimepicker

import plotly.express as px
from plotly import graph_objects as go, graph_objects

import pandas as pd


dates = pd.to_datetime([dt.datetime(2022, 1, 1) + dt.timedelta(days=i) for i in range(365)])
df = pd.DataFrame({
    'dt': dates,
    'data': [random.randint(0, 100) for _ in dates],
    'dt_number': [int((d - dt.datetime(1970, 1, 1)).total_seconds()) for d in dates]
})


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    html.H3("RangeSlider DateTimePicker"),
    dcc.RangeSlider(df['dt_number'].min(), df['dt_number'].max(),
                    value=[df['dt_number'].min(), df['dt_number'].max()], id='my-range-slider',
                    marks={
                        1661990400: {'label': 'Sep'},
                        1640995200: {'label': 'Jan'},
                        1643673600: {'label': 'Feb'},
                        1646092800: {'label': 'Mar'},
                        1648771200: {'label': 'Apr'},
                        1651363200: {'label': 'May'},
                    }),
    dcc.Graph(id='graph-content-1'),
    html.Br(),
    html.H3("Range Picker"),
                dash_datetimepicker.DashDatetimepicker(
                    id="input-range",
                    utc=False,
                    locale="ru",
                    startDate=df['dt'].min(),
                    endDate=df['dt'].max()
                ),
    dcc.Graph(id='graph-content-2'),
])

@callback(
    [Output('graph-content-1', 'figure'),
     Output('graph-content-2', 'figure')],
    [Input('my-range-slider', 'value'),
     Input('input-range', 'startDate'),
     Input('input-range', 'endDate')]
)
def update_graph(slider_value, startDate, endDate):

    print(slider_value, startDate, endDate, type(startDate))
    df_filtered = df[(df['dt_number'] >= slider_value[0]) &
                     (df['dt_number'] <= slider_value[1])]
    fig1 = px.line(df_filtered, x='dt', y='data')
    fig1.update_layout(template='plotly_white')

    #  данные из формы приходят как строка, поэтому необходимо преобразовать в datetime и исключить таймзону
    startDate, endDate = parse(startDate).replace(tzinfo=None), parse(endDate).replace(tzinfo=None)

    df_filtered = df.loc[(df['dt'].dt.to_pydatetime() >= startDate) & (df['dt'].dt.to_pydatetime() <= endDate)]
    fig2 = px.line(df_filtered, x='dt', y='data')
    fig2.update_layout(template='plotly_white')

    return fig1, fig2


if __name__ == '__main__':
    app.run_server(debug=True)