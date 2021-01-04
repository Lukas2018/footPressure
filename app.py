import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import requests
import json
import pandas as pd
import numpy as np
import redis
import plotly.graph_objects as go

from db import Redis

redis = redis.Redis(decode_responses=True)
db = Redis(redis)
db.init_patients()

#sensory zwraca
def get_sensor_values(person_id):
    r = requests.get("http://tesla.iem.pw.edu.pl:9080/v2/monitor/{}".format(person_id))
    sensors = json.loads(r.content)['trace']['sensors']
    return sensors
    
#ten obrazek stopy z sensorami na nim
def feet_image(sensors):
    img_width = 500
    img_height = 600
	
    fig = go.Figure()
    
    fig.add_layout_image(
        dict(
            x=0,
            sizex=img_width,
            y=img_height,
            sizey=img_height,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source="stopa.png")
    )
    
    fig.update_xaxes(
        visible=False,
        range=[0, img_width]
    )

    fig.update_yaxes(
        visible=False,
        range=[0, img_height],
        scaleanchor="x"
    )

    fig.update_layout(
        width=img_width,
        height=img_height,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    
    positions = [(335, 420), (165, 420), (60, 350), (440, 350), (140, 60), (360, 60)]
    for i in range(0, 6):
        fig.add_trace(
            go.Scatter(
                x=[positions[i][0]], y=[positions[i][1]], mode="markers+text", marker = dict(size = 40),
                text = sensors[i]['value'], textfont = dict(color="white")
            )   
        )
    
    return fig

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    className='content',
    children=[
        # Store current person id
        dcc.Store(id='current-person-id', storage_type='session'),
        # Store last anomaly
        dcc.Store(id='last-anomaly'),

        dcc.Interval(id='interval-component',
                     interval=1*1000,
                     n_intervals=0),

        html.Main(className='main-container', children=[
            dcc.Dropdown(
                id='person-dropdown',
                options=[
                    {'label': db.get_patient_personal_data(1), 'value': 1},
                    {'label': db.get_patient_personal_data(2), 'value': 2},
                    {'label': db.get_patient_personal_data(3), 'value': 3},
                    {'label': db.get_patient_personal_data(4), 'value': 4},
                    {'label': db.get_patient_personal_data(5), 'value': 5},
                    {'label': db.get_patient_personal_data(6), 'value': 6},
                ],
                placeholder='Select a person',
            ),
            html.Section(className='visualization-container', children=[
                html.Div(className='foot-container'),
                #niżej na razie przykładowe person id 1, potem z dropdown polaczymy
                dcc.Graph(id='foot_image', config={'displayModeBar': False}, figure=feet_image(get_sensor_values(1)))
            ])
        ]),

        html.Footer(className='footer', children=[
            html.P('PW EE 2020/2021'),
            html.P('Made by: Łukasz Glapiak and Maciej Leszczyński')
        ])
    ])

#callbacks	
@app.callback([Output('current-person-id', 'data')],
              [Input('person-dropdown', 'value')])
def on_person_change(new_person_id):
    return new_person_id

@app.callback(Output('foot_image', 'figure'),
	Input('interval-component', 'n_intervals'))
def update_foot_image(_):
	return feet_image(get_sensor_values(1))

if __name__ == '__main__':
    app.run_server(debug=True)
