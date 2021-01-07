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

redis = redis.Redis(decode_responses=True)
db = Redis(redis)
stat = Stats(db)
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
    
v1, v2, v3, v4, v5, v6 = [], [], [], [], [], []
t1, t2, t3, t4, t5, t6 = [], [], [], [], [], []
temp_values = [v1, v2, v3, v4, v5, v6]
temp_dates = [t1, t2, t3, t4, t5, t6]

    
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
    for i in range(0, 6):
        user = 1 #połączyć z dropdown
        n = 1 #ile wstecz
        values = db.get_user_sensor_values(user, i, n)
        temp_values[i].append(values[0]['value'])
        temp_dates[i].append(values[0]['date'])
        fig.add_trace(go.Scatter(x=temp_dates[i], y=temp_values[i]))
        
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
					options=[
						{'label': 'Sensor 1', 'value': '1'},
						{'label': 'Sensor 2', 'value': '2'},
						{'label': 'Sensor 3', 'value': '3'},
						{'label': 'Sensor 4', 'value': '4'},
						{'label': 'Sensor 5', 'value': '5'},
						{'label': 'Sensor 6', 'value': '6'},
					],
					value=['1', '2', '3', '4', '5', '6'],
					multi=True
				),
                dcc.Graph(id='linear-graph', figure=linear_graph())
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
    Input('interval-component', 'n_intervals'),
    [State('stat-data-table', 'data'), State('stat-data-table', 'columns')]
)
def updateData(n, data, columns):
    
    return data

@app.callback(Output('foot-image', 'figure'),
	Input('interval-component', 'n_intervals'))
def update_foot_image(_):
    db.save_users_sensor_values() #tymczasowo
    return feet_image(get_sensor_values(1))
    
@app.callback(Output('linear-graph', 'figure'),
	Input('interval-component', 'n_intervals'))
def update_linear_graph(_):
	return linear_graph()

if __name__ == '__main__':
    app.run_server(debug=True)
