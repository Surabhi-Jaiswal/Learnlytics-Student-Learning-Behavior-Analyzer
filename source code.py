#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from flask import Flask
from sklearn.linear_model import LinearRegression


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])


students_data = pd.DataFrame(columns=['student_id', 'name', 'progress', 'grades', 'certifications', 'attendance'])


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Student Dashboard"), className="text-center")
    ]),
    dbc.Row([
        dbc.Col(html.H2("Input Section"), className="text-center")
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Add New Student Data"),
            dbc.Input(id="student_name", placeholder="Enter Student Name", type="text"),
            dbc.Input(id="student_progress", placeholder="Enter Progress", type="number"),
            dbc.Input(id="student_grades", placeholder="Enter Grades", type="number"),
            dbc.Input(id="student_certifications", placeholder="Enter Certifications", type="number"),
            dbc.Input(id="student_attendance", placeholder="Enter Attendance", type="number"),
            dbc.Button("Add More", id="add-more-button", color="secondary", className="mt-2"),
            dbc.Button("Generate Dashboard", id="submit-button", color="primary", className="mt-2")
        ])
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="input-message", className="text-center"))
    ]),
    dbc.Row([
        dbc.Col(html.H2("Overall Dashboard"), className="text-center", id="message")
    ]),
    dbc.Row([
        dbc.Col([html.H4("Student Progress (Bar Chart)"), dcc.Graph(id='progress-chart')]),
        dbc.Col([html.H4("Grades Distribution (Pie Chart)"), dcc.Graph(id='grades-chart')])
    ]),
    dbc.Row([
        dbc.Col([html.H4("Certifications (Scatter Plot)"), dcc.Graph(id='certifications-chart')]),
        dbc.Col([html.H4("Attendance (Donut Chart)"), dcc.Graph(id='attendance-chart')])
    ]),
    dbc.Row([
        dbc.Col([html.H4("Mixed Chart (Bar and Line)"), dcc.Graph(id='mixed-chart')])
    ]),
 
    dbc.Row([dbc.Col(html.H2("Single Student Analysis"), className="text-center")]),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="student_selector", placeholder="Enter Student Name for Analysis", type="text"),
            dbc.Button("Analyze Student", id="analyze-button", color="info", className="mt-2"),
        ])
    ]),
    dbc.Row([
        dbc.Col([html.H4("Detailed Student Progress (Bar Chart)"), dcc.Graph(id='single-student-progress-chart')]),
        dbc.Col([html.H4("Areas of Improvement"), html.Div(id="student-improvement-areas", className="mt-2")])
    ])
])


def update_regression_model(df):
    X = df[['progress', 'certifications']]
    y = df['grades']
    regressor = LinearRegression()
    regressor.fit(X, y)
    df['predicted_grades'] = regressor.predict(X)
    return df


@app.callback(
    Output('input-message', 'children'),
    [Input('add-more-button', 'n_clicks')],
    [State('student_name', 'value'),
     State('student_progress', 'value'),
     State('student_grades', 'value'),
     State('student_certifications', 'value'),
     State('student_attendance', 'value')]
)
def add_more_students(n_clicks, name, progress, grades, certifications, attendance):
    global students_data

    if n_clicks and name and progress and grades and certifications and attendance:
       
        new_student = {
            'student_id': len(students_data) + 1,
            'name': name,
            'progress': progress,
            'grades': grades,
            'certifications': certifications,
            'attendance': attendance
        }
        students_data = students_data.append(new_student, ignore_index=True)
        return f"Added {name} to the data. Add more or generate the dashboard."
    return "Please enter all details to add a student."


@app.callback(
    [Output('progress-chart', 'figure'),
     Output('grades-chart', 'figure'),
     Output('certifications-chart', 'figure'),
     Output('attendance-chart', 'figure'),
     Output('mixed-chart', 'figure'),
     Output('message', 'children')],
    Input('submit-button', 'n_clicks')
)
def generate_dashboard(n_clicks):
    global students_data
    if n_clicks and not students_data.empty:
        try:
            
            students_data['progress'] = pd.to_numeric(students_data['progress'], errors='coerce')
            students_data['grades'] = pd.to_numeric(students_data['grades'], errors='coerce')
            students_data['certifications'] = pd.to_numeric(students_data['certifications'], errors='coerce')
            students_data['attendance'] = pd.to_numeric(students_data['attendance'], errors='coerce')

           
            students_data.dropna(subset=['progress', 'grades', 'certifications', 'attendance'], inplace=True)

            if students_data.empty:
                return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "No valid data available to generate the dashboard. Please check the input.")

          
            students_data_updated = update_regression_model(students_data)

       
            progress_fig = px.bar(students_data_updated, x='name', y='progress', title="Student Progress")


            grades_fig = px.pie(students_data_updated, names='name', values='grades', title="Grades Distribution")

           
            certifications_fig = px.scatter(students_data_updated, x='name', y='certifications', size='certifications', color='name', title="Certifications")

            
            attendance_fig = px.pie(students_data_updated, names='name', values='attendance', hole=0.5, title="Attendance")

          
            mixed_fig = go.Figure()
            mixed_fig.add_trace(go.Bar(x=students_data_updated['name'], y=students_data_updated['grades'], name="Grades"))
            mixed_fig.add_trace(go.Scatter(x=students_data_updated['name'], y=students_data_updated['attendance'], mode='lines+markers', name="Attendance"))
            mixed_fig.update_layout(title="Grades (Bar) and Attendance (Line)")

            return (progress_fig, grades_fig, certifications_fig, attendance_fig, mixed_fig, "Dashboard generated for all students.")
        
        except Exception as e:
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Error in generating dashboard: {str(e)}")
    else:
        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "No data available to generate dashboard. Add student details first.")


@app.callback(
    [Output('single-student-progress-chart', 'figure'),
     Output('student-improvement-areas', 'children')],
    Input('analyze-button', 'n_clicks'),
    State('student_selector', 'value')
)
def analyze_single_student(n_clicks, selected_student):
    global students_data
    if n_clicks and selected_student:
        student_data = students_data[students_data['name'] == selected_student]

        if not student_data.empty:
            
            fig = px.bar(student_data, x='name', y=['progress', 'grades', 'attendance'], title=f"{selected_student}'s Performance")

            
            improvements = []
            if student_data.iloc[0]['progress'] < 70:
                improvements.append(f"{selected_student} needs to improve their progress (Current: {student_data.iloc[0]['progress']}%).")
            if student_data.iloc[0]['grades'] < 70:
                improvements.append(f"{selected_student} needs to improve their grades (Current: {student_data.iloc[0]['grades']}%).")
            if student_data.iloc[0]['attendance'] < 80:
                improvements.append(f"{selected_student} needs to improve their attendance (Current: {student_data.iloc[0]['attendance']}%).")

            improvement_message = "Areas of Improvement:\n" + "\n".join(improvements) if improvements else f"{selected_student} is doing well in all areas."

            return fig, improvement_message

    return dash.no_update, "Please select a valid student for analysis."


if __name__ == '__main__':
    app.run_server(debug=True, port=8052)


# In[ ]:





# In[ ]:




