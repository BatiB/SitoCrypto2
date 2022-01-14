from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash
#import dash_html_components as html
import base64
#import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import os
os.chdir('C:/Users/svitali/Desktop/PythonWebsite/SitoCRYPTO')

# must add this line in order for the app to be deployed successfully on Heroku
from app import server
from app import app
# import all pages in the app
#from SitoCRYPTO
import Home1_trial_1, Page_1_trial_1, Page_2_trial_1

# building the navigation bar
# https://github.com/facultyai/dash-bootstrap-components/blob/master/examples/advanced-component-usage/Navbars.py
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="/home", style={'fontSize': 13},),
        dbc.DropdownMenuItem("Crypto Analysis", href="/cryptoanalysis", style={'fontSize': 13},),
        dbc.DropdownMenuItem("Portfolio Analysis", href="/portfolioanalysis", style={'fontSize': 13},),
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
    style={'fontSize': 13},
)

# Logo
image_filename = 'QUANTUMBLOCKAI_1.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="25px")),
                        #dbc.Col(dbc.NavbarBrand('CryptoAnalysis.ai', className="text-left", style={'color': '#3498DB'})), #ml-2
                        dbc.Col(html.Div())
                    ],
                    align="center",
                    #no_gutters=True,
                ),
                href="/home",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    # right align dropdown menu with ml-auto className
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)

# embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/cryptoanalysis':
        return Page_1_trial_1.layout
    elif pathname == '/portfolioanalysis':
        return Page_2_trial_1.layout
    else:
        return Home1_trial_1.layout

if __name__ == '__main__':
    app.run_server(debug=True)