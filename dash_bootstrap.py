import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_daq as daq

import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd
import numpy as np

#conn = sqlite3.connect('twitter.db')
#c = conn.cursor()
# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': "https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css",
        'rel': 'stylesheet',
        'integrity': "sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu",
        'crossorigin': 'anonymous'
    }
]
# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, update_title='Coletando tweets...', 
                    external_stylesheets=[dbc.themes.BOOTSTRAP]
                    #external_scripts=external_scripts
                    )
app.layout = dbc.Container(
    [   html.H1('Bolsometro'),
        html.Hr(),

        dbc.NavbarSimple(
            children=[
                #dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Redes Sociais", header=True),
                        dbc.DropdownMenuItem("Linkedin", href="https://www.linkedin.com/in/neto-figueira/"),
                        dbc.DropdownMenuItem("Github", href="https://github.com/netofigueira"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Contato",
                ),
            ],
            brand="Estão falando mal de mim?",
            brand_href="#",
            color="dark",
            dark=True,
        ),


            
        



        dbc.Card(
            id='card', 
            children=[dbc.CardImg(src='/assets/bolso_drawn.png',
             style={"width": 1100, "height": 400,'textAlign':'center'},
                           className='card-img-bottom'),
                dbc.CardHeader("Análise da popularidade do presidente Bolsonaro em tempo real", id='header'),
                dbc.Button(
                    "Como funciona", id="popover-target", color="dark"
                ),
                dbc.Popover(
                    [
                        dbc.PopoverHeader("Medidores"),
                        dbc.PopoverBody("A análise textual é feita através do Léxico para Inferência Adaptada (LeIA) "\
                                        "Cada tweet retorna um valor escalado entre -10 (extremamente negativo) e 10 (extremamente positivo)"\
                                        "o gráfico a direita mostra a média de sentimento dos ultimos tweets a cada segundo. " \
                                        "o medidor à esquerda faz a média dos ultimos 500 tweets negativos apenas,"\
                                        "e mostra o resultado numa escala de 0 a 10 de negatividade"\
                                ),
                    ],
                    id="popover",
                    is_open=False,
                    target="header",
                ),          
            ]
            ),


            dbc.Row(className='row', 
                    children=[dbc.Col(dcc.Graph(id='live-graph', animate=True) ),
                              dbc.Col(html.Div(dcc.Graph(id='my-gauge', animate=True)) ),
                                                                
                                                                 ]),
            dcc.Interval(
                id='graph-update',
                interval= 800,
            ),
            dcc.Interval(
                id='my-gauge-update',
                interval= 800,
            ),            

        html.Div(html.H2('Tweets mais Negativos')),
        html.Hr(),
        html.Div(className='row', children=[html.Div(id="recent-tweets-table")] ),


        dcc.Interval(
            id='recent-table-update',
            interval= 4*10**3,
            #n_intervals=2
        ),
    ]
)

def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ],
                                                                        )
                               for d in df.values.tolist()])
                          ]
    )



@app.callback(
    Output("popover", "is_open"),
    [Input("popover-target", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(Output('my-gauge', 'figure'),
                [Input('my-gauge-update', 'n_intervals')])

def update_gauge(input_data):
    try:
        conn = sqlite3.connect('twitter.db')
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix DESC LIMIT 500", conn)
        df.sort_values('unix', inplace=True)
        s_array = df.sentiment.values
        df['sentiment'] = np.interp(s_array, (s_array.min(), s_array.max()), (-10,10) )

        neg = np.abs(df[(df.sentiment < 0)].sentiment.mean())

        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/100)).mean()

        fig = go.Indicator(
            mode = "gauge+number",
            value = neg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Bolsometro"},
            #delta = {'reference': 8, 'increasing': {'color': "Green"}},
            gauge = {
                'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#EF553B"},
                'bar': {'color': "#453938"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 5], 'color': 'white'},
                    {'range': [5, 6.5], 'color': '#ffb0a8'},
                    {'range': [6.5, 8], 'color': '#EF553B'}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 9}}
        )
        return {'data': [fig]}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')
    
@app.callback(Output('live-graph', 'figure'),
                [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)

        s_array = df.sentiment.values
        df['sentiment'] = np.interp(s_array, (s_array.min(), s_array.max()), (-10,10) )

        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/10)).mean()
        df.dropna(inplace=True)
        df['date'] = pd.to_datetime(df['unix'],unit='ms')
        # converting to são paulo time. 
        df['date'] = df.date.dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
        df.set_index('date', inplace=True)

        df = df.resample('10s').mean()
        X = df.index
        Y = df.sentiment_smoothed.round(decimals=2)

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-5,5]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('recent-tweets-table', 'children'),
              [Input('recent-table-update', 'n_intervals')],
              )        
def update_recent_tweets(input_data):
    conn = sqlite3.connect('twitter.db')
    c = conn.cursor()

    df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix DESC LIMIT 10", conn)

    df['date'] = pd.to_datetime(df['unix'], unit='ms')
    s_array = df.sentiment.values
    df['sentiment'] = np.interp(s_array, (s_array.min(), s_array.max()), (-10,10) )
    df['sentiment'] = df.sentiment.round(2)
    df = df.drop(['unix'], axis=1)
    df = df[['date','tweet','sentiment']]
    # converting to são paulo time. 
    df['date'] = df.date.dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
    df.set_index('date', inplace=True)
    df = df[(df.sentiment < -0.4)]
    return generate_table(df, max_rows=10)


#external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css"]
#for css in external_css:
#    app.css.append_css({"external_url": css})



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8058, debug=True)