import os
import dash
import dash_core_components as dcc
import dash_html_components as html

import requests
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    className='content',
    children=[
        # Store current person id
        dcc.Store(id='current-id', storage_type='session'),
        # Store last anomaly
        dcc.Store(id='last-anomaly'),

        dcc.Interval(id='interval-component',
                     interval=1*1000,
                     n_intervals=0),

        html.Main(className='main-container', children=[
            dcc.Dropdown(
                id='person-dropdown',
                options=[
                    {'label': 'Person 0', 'value': 0},
                    {'label': 'Person 1', 'value': 1},
                    {'label': 'Person 2', 'value': 2},
                    {'label': 'Person 3', 'value': 3},
                    {'label': 'Person 4', 'value': 4},
                    {'label': 'Person 5', 'value': 5},
                ],
                placeholder='Select a person',
            ),
            html.Section(className='visualization-container', children=[
                html.Div(className='foot-container'),
            ])
        ]),

        html.Footer(className='footer', children=[
            html.P('PW EE 2020/2021'),
            html.P('Made by: Łukasz Glapiak and Maciej Leszczyński')
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)