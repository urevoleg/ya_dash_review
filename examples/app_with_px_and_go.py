from dash import Dash, html, dcc, callback, Output, Input

import plotly.express as px
from plotly import graph_objects as go
import plotly.figure_factory as ff

import pandas as pd

df = pd.read_excel("https://github.com/urevoleg/example-direct-access/blob/main/Sample%20-%20Superstore.xlsx?raw=true")


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df['Region'].unique(), 'South', id='dropdown-selection-1'),
    dcc.Graph(id='graph-content-1'),
    dcc.Graph(id='graph-content-2'),
    dcc.Dropdown(df['City'].unique(), 'Henderson', id='dropdown-selection-2'),
    dcc.Graph(id='graph-content-3')
])

@callback(
    [Output('graph-content-1', 'figure'),
     Output('graph-content-2', 'figure'),
     Output('graph-content-3', 'figure')],
    [Input('dropdown-selection-1', 'value'),
     Input('dropdown-selection-2', 'value')]
)
def update_graph(region, city):
    dff = df[df['Region']==region]
    fig1 = px.line(dff.groupby('Ship Date', as_index=False).agg({'Order ID': 'nunique'}), x='Ship Date', y='Order ID')
    fig1.update_layout(template='plotly_white')

    fig2 = go.Figure(data=[go.Box(x=dff['Sub-Category'], y=dff['Sales'])])
    fig2.update_layout(template='plotly_white')

    df_table = df[df['City']==city].pivot_table(columns='Category', index='Sub-Category', values='Sales', aggfunc='mean', fill_value=0).round(1)
    fig3 = ff.create_annotated_heatmap(z=df_table.values.tolist(), x=df_table.columns.tolist(), y=df_table.index.tolist())
    fig3.update_layout(template='plotly_white',
                       height=720)

    return fig1, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)