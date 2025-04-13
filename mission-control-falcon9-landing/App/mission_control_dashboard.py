"""
Launch Performance Dashboard
------------------------

This Dash app provides an interactive view of SpaceX Falcon 9 launch records.
Users can explore:

- A pie chart showing success vs. failure by launch site
- A scatter plot of payload mass vs. landing outcome

Usage Instructions:
1. Open terminal and navigate to the app folder:
   cd app

2. Run the Dash app:
   python mission_control_dashboard.py

Requirements:
- Python
- dash
- pandas
- plotly

Dataset:
- spacex_launch_dash.csv (located in app/data/)
"""


# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch dataset
spacex_df = pd.read_csv("data/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Launch Site Dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    
    html.Br(),
    
    # Pie chart showing launch success distribution
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Payload mass range slider
    html.P("Payload Range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2000)},
                    value=[min_payload, max_payload]),
    
    html.Br(),
    
    # Scatter plot: Payload vs Outcome
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
],
style={'textAlign': 'center', 'margin': 'auto', 'width': '80%'})

# Callback: Update pie chart based on selected launch site
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate total successful launches by site
        filtered_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            filtered_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site',
            color='Launch Site',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
    else:
        # Filter for selected site and count success vs failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df.groupby('class').size().reset_index(name='Count')
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Success vs Failure Outcomes at {entered_site}',
            color='Outcome',
            color_discrete_map={'Success': 'green', 'Failure': 'red'}
        )

    return fig


# Callback for scatter plot based on site and payload
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def get_scatter_plot(entered_site, payload_range):
    # Filter by payload
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Filter by site if not ALL
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     color_discrete_sequence=px.colors.qualitative.Set1,
                     title=f'Payload vs Outcome for {"All Sites" if entered_site == "ALL" else entered_site}',
                     labels={'class': 'Launch Outcome (1 = Success, 0 = Failure)'})
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
