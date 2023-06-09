# Dash и Datetime Filter

Привет, пытливый читатель🙌

## Вопросы
![](https://cdn.lifehacker.ru/wp-content/uploads/2016/02/Depositphotos_10817575_l-2015_1454341702-630x446.jpg)

**1. Фильтр для времени.**

Возможны кастомные решения из доступных компонентов:
- в примере `examples/app_filter_timeline.py` показана реализация с [RangeSlider](https://dash.plotly.com/dash-core-components/rangeslider). 
Переводим `datetime` в числа и работает с ними.  Пример реализован для дней, вариант рабочий, 
но сложность в том, что пока частей по времени мало (например, недельные данные
за каждый день, то их можно отобразить на слайдере (аргумент `marks`)), но когда их много, то будет каша.
И опять нужно выкручиваться, например, добавлять блок `Label` и туда выводить текущие выбранные границы.

Пример с отображением месяцев:

```python
marks={
                        1661990400: {'label': 'Sep'},
                        1640995200: {'label': 'Jan'},
                        1643673600: {'label': 'Feb'},
                        1646092800: {'label': 'Mar'},
                        1648771200: {'label': 'Apr'},
                        1651363200: {'label': 'May'},
                    }
```

Результат:
![Screenshot from 2023-03-29 15-02-18.png](img%2FScreenshot%20from%202023-03-29%2015-02-18.png)


Нашлось еще решение:
- [dash_datetimepicker](https://github.com/SebastianRehfeldt/dash-datepicker/blob/master/dash_datetimepicker/usage.py)

В пример `examples/app_filter_timeline.py` он тоже добавлен.

Выглядит это так:
Дата:
![Screenshot from 2023-03-29 14-12-54.png](img%2FScreenshot%20from%202023-03-29%2014-12-54.png)

Время:
![Screenshot from 2023-03-29 14-13-03.png](img%2FScreenshot%20from%202023-03-29%2014-13-03.png)


------------------------------------
**2. plotly px и go явно работают как-то по разному, но как именно?**

`px` - `plotly_express`.

Для построения графика необходим объект `figure` (чтобы его можно было вернуть из функции, это соответствует  `Output('total_events', 'figure')`).

Объект можно получить несколькими способами:
- при помощи библиотеки `plotly_express`

```python
fig = px.line(dff, x='year', y='pop')
```

- или при помощи основной библиотеки `plotly` и её модуля `graph_objects`

```python
fig = go.Figure(data=[go.Scatter()])
```

- или при помощи основной библиотеки `plotly` и её модуля `figure_factory`

```python
fig = ff.create_annotated_heatmap()
```

Библиотека `plotly_express` фактически является простой оберткой над `plotly`,  
тк нет необходимости описывать сложную структуру для формирования визуализации. При этом `plotly_express`
имеет `seaborn`-like стиль получение конечной визуализации.

Можно провести такое сравнение: если `plotly` - это `matplotlib`, то 
`plotly_express` - `seaborn`.

Объект `figure`, представляет из себя словарь c полным описание того, как построить визуализацию. Посмотреть что внутри, можно так:

```python
import json
from pprint import pprint

from plotly.utils import PlotlyJSONEncoder


graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
pprint(graphJSON)
```

Каким образом получен этот объект - не важно. Дашборд `examples/app_with_px_and_go.py` демонстрирует
формирование `figure` тремя способами.

Главное, чтобы было соответствие:
- кол-ва html-объектов (3 штуки `dcc.Graph`):

```python
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df['Region'].unique(), 'South', id='dropdown-selection-1'),
    dcc.Graph(id='graph-content-1'),
    dcc.Graph(id='graph-content-2'),
    dcc.Dropdown(df['City'].unique(), 'Henderson', id='dropdown-selection-2'),
    dcc.Graph(id='graph-content-3')
])
```

- кол-ва Output у функции, которая отрисовывает графики (3 штуки `Output('graph-content-1', 'figure')`):
- 
```python
@callback(
    [Output('graph-content-1', 'figure'),
     Output('graph-content-2', 'figure'),
     Output('graph-content-3', 'figure')],
    [Input('dropdown-selection-1', 'value'),
     Input('dropdown-selection-2', 'value')]
)
```
- кол-ва объектов, которые возвращает функция (3 штуки `fig1, fig2, fig3`):

```python
    ...
    return fig1, fig2, fig3

```

ps: Перечисление через запятую в `return` означает, что возращается () (tuple), то есть это эквивалентно записи `return (fig1, fig2, fig3)`, 
но так не принято писать.

Комбинации `Ouput()\Input()` объектов позволяют разделять дашборд на части, реагирующие только на определенные управляющие элементы.

В примере выше, есть 2 DropDown элемента - оба указаны в функции, которая содержит 3 Output - это означает, что изменение любого из DropDown будет
влиять на каждый из графиков. Если такое поведение не требуется, то можно что-то исключить:
- можно оставить только 1 DropDown
- или оставить 1 график - тогда 2 DropDown будут управлять 1 графиком
- если разделить функцию на 2, и в каждой оставить разные DropDown и разные наборы графиков, то получатся две назависимые части дашборда
