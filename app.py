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
db.save_users_sensor_values()

#sensory zwraca
def get_sensor_values(person_id):
    sensors = []
    sensors.append(db.get_user_sensor_values(person_id, 0, 1)[0])
    sensors.append(db.get_user_sensor_values(person_id, 1, 1)[0])
    sensors.append(db.get_user_sensor_values(person_id, 2, 1)[0])
    sensors.append(db.get_user_sensor_values(person_id, 3, 1)[0])
    sensors.append(db.get_user_sensor_values(person_id, 4, 1)[0])
    sensors.append(db.get_user_sensor_values(person_id, 5, 1)[0])
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
            source=app.get_asset_url('stopa.png'))
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
    

def linear_graph():
    fig = go.Figure()
    for sensor in range(1, 7):
        user = 1 #połączyć z dropdown
        n = 10 #ile wstecz
        values = db.get_user_sensor_values(user, sensor, n)
        #fig.add_trace(go.Scatter(x=0, y=np.array(sensor['value'])))
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
                value='1',
                placeholder='Select a person'
            ),
            html.Section(className='visualization-container', children=[
                html.Div(className='foot-container'),
                #niżej na razie przykładowe person id 1, potem z dropdown polaczymy
                dcc.Graph(id='foot-image', config={'displayModeBar': False}, figure=feet_image(get_sensor_values(1))),
                dcc.Graph(id='linear-graph', figure=linear_graph())
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

@app.callback(Output('foot-image', 'figure'),
	Input('interval-component', 'n_intervals'))
def update_foot_image(_):
    db.save_users_sensor_values() #tymczasowo
    return feet_image(get_sensor_values(1))
    
@app.callback(Output('linear-graph', 'figure'),
	Input('interval-component', 'n_intervals'))
def update_linear_graph(_):
	return linear_graph(get_sensor_values(1))

if __name__ == '__main__':
    app.run_server(debug=True)
