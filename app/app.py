import os
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import requests
import json
import pandas as pd
import numpy as np
import redis
import plotly.graph_objects as go

from statistics import Stats
from db import Redis
from config import Config

REDIS_NAME = os.getenv('REDIS_NAME') or 'localhost'
redis = redis.Redis(REDIS_NAME, decode_responses=True)
config = Config(6, 6)
db = Redis(redis, config)
stat = Stats(db)
db.init_patients()
db.save_users_sensor_values()

#sensory zwraca
def get_sensor_values(person_id):
    sensors = []
    for i in range(0, config.get_sensors_number()):
        sensors.append(db.get_user_sensor_data(person_id, i, 1)[0])
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
    for i in range(0, config.get_sensors_number()):
        fig.add_trace(
            go.Scatter(
                x=[positions[i][0]], y=[positions[i][1]], mode="markers+text", marker = dict(size = 40),
                text = sensors[i]['value'], textfont = dict(color="white")
            )   
        )
    
    return fig
  
def fetch_data(person_id, n):
	data = []
	dates = []
	for sensor in range(0, 6):
		data.append(db.get_user_sensor_data(person_id, sensor, n, 'value'))
		dates.append(db.get_user_sensor_data(person_id, sensor, n, 'date'))
	
	return [data, dates]
		
def linear_graph(person_id, sensor_values, n, values):
	data = values[0]
	dates = values[1]
	fig = go.Figure()
	for sensor in sensor_values:
		#data = db.get_user_sensor_data(person_id, sensor, 5, 'value')
		#dates = db.get_user_sensor_data(person_id, sensor, 5, 'date')
		fig.add_trace(go.Scatter(x=dates[sensor], y=data[sensor], line_shape='spline'))
 
	fig.update_xaxes(
		tickangle = 55)
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

        dcc.Interval(id='update-component',
                     interval=1*2000,
                     n_intervals=0),
        dcc.Interval(id='download-component',
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
                value=1,
                placeholder='Select a person'
            ),
            html.Section(className='visualization-container', children=[
                #niżej na razie przykładowe person id 1, potem z dropdown polaczymy
                dash_table.DataTable(
                    id='stat-data-table',
                    style_cell={
                        'textAlign': 'center',
                        'maxWidth': 0
                    },
                    columns=[{
                        'name': '',
                        'id': 'stat-name'
                    },    
                    {
                        'name': 'L1',
                        'id': 'l1'
                    }, 
                    {
                        'name': 'L2',
                        'id': 'l2'
                    },
                    {
                        'name': 'L3',
                        'id': 'l3'
                    },
                    {
                        'name': 'R1',
                        'id': 'r1'
                    },
                    {
                        'name': 'R2',
                        'id': 'r2'
                    },
                    {
                        'name': 'R3',
                        'id': 'r3'
                    }],
                    data=[{
                        'stat-name': 'Minimum',
                        'l1': 11,
                        'l2': 12,
                        'l3': 13,
                        'r1': 14,
                        'r2': 15,
                        'r3': 16
                    },
                    {
                        'stat-name': 'Maximum',
                        'l1': 16,
                        'l2': 15,
                        'l3': 14,
                        'r1': 13,
                        'r2': 12,
                        'r3': 11
                    },
                    {
                        'stat-name': 'Mean',
                        'l1': 13,
                        'l2': 13,
                        'l3': 13,
                        'r1': 13,
                        'r2': 13,
                        'r3': 13
                    },
                    {
                        'stat-name': 'Root Mean Square',
                        'l1': 1,
                        'l2': 2,
                        'l3': 3,
                        'r1': 4,
                        'r2': 5,
                        'r3': 6
                    }]
                ),
                html.Div(className='foot-anomaly-container', children=[
                    dcc.Graph(id='foot-image', config={'displayModeBar': False}, figure=feet_image(get_sensor_values(1))),
                    html.Div(className='anomaly-container', children=[
                        html.H3('Anomaly counter'),
                        html.Div(children=[
                            html.P('L1:'),
                            html.P('56')
                        ]),
                        html.Div(children=[
                            html.P('L2:'),
                            html.P('26')
                        ]),
                        html.Div(children=[
                            html.P('L3:'),
                            html.P('16')
                        ]),
                        html.Div(children=[
                            html.P('L4:'),
                            html.P('45')
                        ]),
                        html.Div(children=[
                            html.P('L5:'),
                            html.P('12')
                        ]),
                        html.Div(children=[
                            html.P('L6:'),
                            html.P('14')
                        ]),
                    ])
                ]),
                dcc.Dropdown(
					id='sensor-dropdown',
					options=[
						{'label': 'Sensor 1', 'value': 0},
						{'label': 'Sensor 2', 'value': 1},
						{'label': 'Sensor 3', 'value': 2},
						{'label': 'Sensor 4', 'value': 3},
						{'label': 'Sensor 5', 'value': 4},
						{'label': 'Sensor 6', 'value': 5},
					],
					value=[0, 1, 2, 3, 4, 5],
					multi=True
				),
                #dcc.Graph(id='linear-graph', figure=linear_graph(1, [0, 1, 2, 3, 4, 5]))
                dcc.Graph(id='linear-graph')
            ])
        ]),
		html.Footer(className='footer', children=[
            html.P('PW EE 2020/2021'),
            html.P('Made by: Łukasz Glapiak and Maciej Leszczyński')
        ])
    ])

#callbacks	
@app.callback(Output('current-person-id', 'data'),
    Input('person-dropdown', 'value'))
def on_person_change(new_person_id):
	return new_person_id

@app.callback(Output('stat-data-table', 'data'),
    Input('update-component', 'n_intervals'),
    [State('stat-data-table', 'data'), State('stat-data-table', 'columns')]
)
def updateData(n, data, columns):
    
    return data

@app.callback(Output('foot-image', 'figure'),
	[Input('update-component', 'n_intervals'),
	Input('person-dropdown', 'value')])
def update_foot_image(_, dropdown_value):
    db.save_users_sensor_values() #tymczasowo
    return feet_image(get_sensor_values(dropdown_value))
    
@app.callback(Output('linear-graph', 'figure'),
	[Input('update-component', 'n_intervals'),
	Input('download-component', 'n_intervals'),
    Input('person-dropdown', 'value'),
    Input('sensor-dropdown', 'value')])
def update_linear_graph(up, down, person, sensors):
	values = fetch_data(person, down)
	return linear_graph(person, sensors, up, values)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
