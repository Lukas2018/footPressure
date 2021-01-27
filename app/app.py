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
sensor_names = ['L1', 'L2', 'L3', 'R1', 'R2', 'R3']

#sensory zwraca
def get_sensor_values(person_id):
    sensors = []
    for i in range(0, config.get_sensors_number()):
        sensors.append(db.get_user_sensor_data(person_id, i, 1)[0])
    print(db.get_anomaly_counts())
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
        width=img_width-20,
        height=img_height-108,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )
    
    positions = [(165, 420), (60, 350), (140, 60), (335, 420), (440, 350), (360, 60)]
    for i in range(0, config.get_sensors_number()):
        if (int)(sensors[i]['value']) < 600:
            size = 30
        else:
            size = (int)(sensors[i]['value'])/18
        fig.add_trace(
            go.Scatter(
                x=[positions[i][0]], y=[positions[i][1]], mode="markers+text", marker = dict(size = size),
                text = sensors[i]['value'], textfont = dict(color="white"), name = sensor_names[i]
            )   
        )
    
    return fig
  
def fetch_data(person_id, n):
	data = []
	dates = []
	for sensor in range(0, config.get_sensors_number()):
		data.append(db.get_user_sensor_data(person_id, sensor, n, 'value'))
		dates.append(db.get_user_sensor_data(person_id, sensor, n, 'date'))
	return [data, dates]
		
def linear_graph(sensor_values, values):
	data = values[0]
	dates = values[1]
	fig = go.Figure()
	for sensor in sensor_values:
		fig.add_trace(go.Scatter(x=dates[sensor], y=data[sensor], name=sensor_names[sensor]))
 
	fig.update_xaxes(
		tickangle = 55)
		
	fig.update_layout(height=350)
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
                        'name': 'Sensor',
                        'id': 'stat-name'
                    },    
                    {
                        'name': 'L1',
                        'id': '0'
                    }, 
                    {
                        'name': 'L2',
                        'id': '1'
                    },
                    {
                        'name': 'L3',
                        'id': '2'
                    },
                    {
                        'name': 'R1',
                        'id': '3'
                    },
                    {
                        'name': 'R2',
                        'id': '4'
                    },
                    {
                        'name': 'R3',
                        'id': '5'
                    }],
                    data=[{
                        'stat-name': 'Minimum',
                        '0': 1023,
                        '1': 1023,
                        '2': 1023,
                        '3': 1023,
                        '4': 1023,
                        '5': 1023
                    },
                    {
                        'stat-name': 'Maximum',
                        '0': 1023,
                        '1': 1023,
                        '2': 1023,
                        '3': 1023,
                        '4': 1023,
                        '5': 1023
                    },
                    {
                        'stat-name': 'Mean',
                        '0': 1023,
                        '1': 1023,
                        '2': 1023,
                        '3': 1023,
                        '4': 1023,
                        '5': 1023
                    },
                    {
                        'stat-name': 'Root Mean Square',
                        '0': 1023,
                        '1': 1023,
                        '2': 1023,
                        '3': 1023,
                        '4': 1023,
                        '5': 1023
                    }]
                ),
                dcc.Dropdown(
					id='sensor-dropdown',
					options=[
						{'label': 'Sensor L1', 'value': 0},
						{'label': 'Sensor L2', 'value': 1},
						{'label': 'Sensor L3', 'value': 2},
						{'label': 'Sensor R1', 'value': 3},
						{'label': 'Sensor R2', 'value': 4},
						{'label': 'Sensor R3', 'value': 5},
					],
					value=[0, 1, 2, 3, 4, 5],
					multi=True
				),
                dcc.Graph(id='linear-graph'),
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
                
                #dcc.Graph(id='linear-graph', figure=linear_graph(1, [0, 1, 2, 3, 4, 5]))
                
            ])
        ]),
        html.Div(id='hidden-div', style={'display':'none'}),
		html.Footer(className='footer', children=[
            html.P('PW EE 2020/2021'),
            html.P('Made by: Łukasz Glapiak and Maciej Leszczyński')
        ])
    ])

@app.callback(Output('hidden-div', 'children'),
    Input('update-component', 'n_intervals'))
def get_data_from_api(_):
    db.save_users_sensor_values()
    return ''


@app.callback(Output('current-person-id', 'data'),
    Input('person-dropdown', 'value'))
def on_person_change(new_person_id):
	return new_person_id

@app.callback(Output('stat-data-table', 'data'),
    [Input('update-component', 'n_intervals'),
    Input('person-dropdown', 'value')],
    [State('stat-data-table', 'data'), State('stat-data-table', 'columns')]
)
def updateData(n, person_id, data, columns):
    for i in range(0, config.get_sensors_number()):
        data[0][str(i)] = stat.min(person_id, i)
    for i in range(0, config.get_sensors_number()):
        data[1][str(i)] = stat.max(person_id, i)
    for i in range(0, config.get_sensors_number()):
        data[2][str(i)] = stat.mean(person_id, i)
    for i in range(0, config.get_sensors_number()):
        data[3][str(i)] = stat.rms(person_id, i)
    return data

@app.callback(Output('foot-image', 'figure'),
	[Input('update-component', 'n_intervals'),
	Input('person-dropdown', 'value')])
def update_foot_image(_, dropdown_value):
    return feet_image(get_sensor_values(dropdown_value))
    
@app.callback(Output('linear-graph', 'figure'),
	[Input('update-component', 'n_intervals'),
    Input('person-dropdown', 'value'),
    Input('sensor-dropdown', 'value')])
def update_linear_graph(up, person, sensors):
	values = fetch_data(person, 20)
	return linear_graph(sensors, values)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
