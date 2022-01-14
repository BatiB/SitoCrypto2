import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# bootstrap theme
# https://bootswatch.com/lux/
external_stylesheets = [dbc.themes.DARKLY]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True


# meta_tags are required for the app layout to be mobile responsive
'''
app = dash.Dash(__name__, suppress_callback_exceptions=external_stylesheets,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server
app.config.suppress_callback_exceptions = True
'''