# Импорт библиотек
import os

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import plotly.figure_factory as ff

# Константы

PATH = os.path.dirname(os.path.realpath(__file__))  # путь к файлу с данными для импорта
SOURCE_DATA = 'dash_visits.csv'  # имя файла с исходными данными
HOST = '127.0.0.1'  # дашборд запуститься на локальной машине
PORT = 3000  # порт


# Функции

def import_data(PATH, SOURCE_DATA):
    try:
        df = pd.read_csv(os.path.join(PATH, SOURCE_DATA), delimiter=',')
        df['dt'] = pd.to_datetime(df['dt'])
        return df
    except Exception as e:
        print('Ошибка при импорте файлов! Проверьте путь и названия файлов!')
        print(e)
        df['dt'] = pd.to_datetime(df['dt'])
        return None


# Импорт данных
df = import_data(PATH, SOURCE_DATA)

# Лейаут дашборда
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, compress=False)
app.layout = html.Div(children=[
    html.Div([  # ROW 1: NAME AND DT FILTER
        html.Div([
            html.Label('Анализ взаимодействия пользователей с карточками Яндекс.Дзен'),
        ], className='six columns'),

        html.Div([
            html.Label('Фильтр по дате и времени:'),
            dcc.Input(
                id="start_time_h",
                type="number",
                value=0,
                min=0,
                max=24,
                step=1,
            ),
            dcc.Input(
                id="start_time_m",
                type="number",
                value=0,
                min=0,
                max=59,
                step=1,
            ),
            dcc.DatePickerRange(
                start_date=df['dt'].dt.date.min(),
                end_date=df['dt'].dt.date.max(),
                display_format='YYYY-MM-DD',
                id='dt_selector',
            ),
            dcc.Input(
                id="end_time_h",
                type="number",
                value=23,
                min=0,
                max=24,
                step=1,
            ),
            dcc.Input(
                id="end_time_m",
                type="number",
                value=59,
                min=0,
                max=59,
                step=1,
            ),
        ], className='six columns'),

    ], className='row'),

    html.Div([  # ROW 2: DESCRIPTION, THEME FILTER, AGE FILTER
        html.Div([
            html.Label('Источники данных для дашборда: таблица dash_visits, которую предоставили дата-инженеры;'),
            html.Label('Частота обновления данных: один раз в сутки, в полночь по UTC.'),
        ], className='six columns'),

        html.Div([
            html.Label('Фильтр по темам карточек'),
            dcc.Dropdown(
                options=[{'label': x, 'value': x} for x in df['item_topic'].unique()],
                value=df['item_topic'].unique().tolist(),
                multi=True,
                id='theme_selector'
            ),
        ], className='three columns'),

        html.Div([
            html.Label('Фильтр по возрастным категориям'),
            dcc.Dropdown(
                options=[{'label': x, 'value': x} for x in df['age_segment'].unique()],
                value=df['age_segment'].unique().tolist(),
                multi=True,
                id='age_selector'
            ),
        ], className='three columns'),

    ], className='row'),

    html.Div([  # ROW 3: Graph: Events, Graph: EVENT PER THEME, Graph: EVENT PER SOURCE
        html.Div([
            html.Label('События по темам карточек'),
            dcc.Graph(
                style={'height': '25vw'},
                id='total_events',
            ),
        ], className='four columns'),

        html.Div([
            html.Label('% событий по темам карточек'),
            dcc.Graph(
                style={'height': '25vw'},
                id='themed_events',
            ),
        ], className='four columns'),

        html.Div([
            html.Label('События по темам источников'),
            dcc.Graph(
                style={'height': '25vw'},
                id='events_by_source',
            ),
        ], className='four columns'),

    ], className='row'),

    html.Div([  # ROW 4: TABLE
        html.Div([
            html.Label('Темы источников - темы карточек'),
            dcc.Graph(
                style={'height': '25vw'},
                id='big_table',
                figure={},
            ),
        ], className='twelve columns'),
    ], className='row'),

])


# Логика дашборда
@app.callback(
    [Output('total_events', 'figure'),
     Output('themed_events', 'figure'),
     Output('events_by_source', 'figure'),
     ],
    [Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
     Input('start_time_h', 'value'),
     Input('start_time_m', 'value'),
     Input('end_time_h', 'value'),
     Input('end_time_m', 'value'),
     Input('theme_selector', 'value'),
     Input('age_selector', 'value'),
     ])
def update_figures(start_date, end_date, start_time_h, start_time_m, end_time_h, end_time_m, theme, age):
    filtered = df.query(
        'item_topic in @theme'
    )
    filtered = filtered.query(
        'age_segment in @age'
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if start_date == end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59)
    try:
        start_date = start_date.replace(hour=int(start_time_h), minute=int(start_time_m))
        end_date = end_date.replace(hour=int(end_time_h), minute=int(end_time_m))
    except Exception as e:
        print(e)

    filtered = filtered.query(
        'dt >= @start_date and dt <= @end_date'
    )

    # События по темам источников DONE
    df_events_by_source = (
        filtered
        .groupby('source_topic')['visits']
        .sum()
        .div(filtered['visits'].sum())
        .mul(100)
    )
    events_by_source = [go.Pie(labels=df_events_by_source.index,
                               values=df_events_by_source.values,
                               name='sources')]

    # События по темам карточек DONE
    df_total_events = (
        filtered
        .groupby(['dt', 'item_topic'])
        .agg({'visits': 'sum'})
        .reset_index()
    )
    total_events = []
    for item in df_total_events['item_topic'].unique():
        total_events += (
            [
                go.Scatter(
                    x=df_total_events.query('item_topic == @item')['dt'],
                    y=df_total_events.query('item_topic == @item')['visits'],
                    mode='lines',
                    stackgroup='one',
                    name=item)
            ]
        )

        # % событий по темам карточек DONE
    total = (
        df_total_events.groupby('dt')
        .agg({'visits': 'sum'})
        .rename(columns={'visits': 'total_visits'})
    )
    df_percent_events = (
        df_total_events.set_index('dt')
        .join(total)
        .reset_index()
    )
    df_percent_events['visits'] = (
            df_percent_events['visits'] / df_percent_events['total_visits']
    )

    percent_events = []
    for item in df_total_events['item_topic'].unique():
        percent_events += (
            [
                go.Scatter(
                    x=df_percent_events.query('item_topic == @item')['dt'],
                    y=df_percent_events.query('item_topic == @item')['visits'],
                    mode='lines',
                    stackgroup='one',
                    name=item)
            ]
        )

    return (
        {  # total_events DONE
            'data': total_events,
            'layout': go.Layout(xaxis={'title': 'Время'},
                                )
        },
        {  # themed_events DONE
            'data': percent_events,
            'layout': go.Layout(xaxis={'title': 'Время'},
                                )
        },
        {  # events_by_source DONE
            'data': events_by_source,
            'layout': go.Layout()
        },
    )


@app.callback(
    Output('big_table', 'figure'),
    [Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
     Input('start_time_h', 'value'),
     Input('start_time_m', 'value'),
     Input('end_time_h', 'value'),
     Input('end_time_m', 'value'),
     Input('theme_selector', 'value'),
     Input('age_selector', 'value'),
     ])
def update_table(start_date, end_date, start_time_h, start_time_m, end_time_h, end_time_m, theme, age):
    filtered = df.query(
        'item_topic in @theme'
    )
    filtered = filtered.query(
        'age_segment in @age'
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if start_date == end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59)
    try:
        start_date = start_date.replace(hour=int(start_time_h), minute=int(start_time_m))
        end_date = end_date.replace(hour=int(end_time_h), minute=int(end_time_m))
    except:
        pass

    filtered = filtered.query(
        'dt >= @start_date and dt <= @end_date'
    )

    df_big_table = (
        filtered
        .pivot_table(
            index='source_topic',
            columns='item_topic',
            values='visits',
            aggfunc='sum')
        .fillna(0)
    )
    z = df_big_table.values.tolist()
    x = df_big_table.columns.tolist()
    y = df_big_table.index.tolist()
    big_table = (
        ff.create_annotated_heatmap(
            z,
            x=x,
            y=y,
            annotation_text=z,
            colorscale='viridis',
            name='big_table'
        )
    )
    return big_table


if __name__ == '__main__':
    app.run_server(host=HOST,
                   port=PORT,
                   debug=False,
                   use_reloader=False,
                   dev_tools_props_check=False
                   )