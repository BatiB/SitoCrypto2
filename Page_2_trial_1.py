# -------------------------------------------------------------------------------------------
#                                       *** SOURCES ***
# -------------------------------------------------------------------------------------------
# https://towardsdatascience.com/build-a-web-data-dashboard-in-just-minutes-with-python-d722076aee2b
# https://youtube.com/watch?v=wYvx8K-nzg4&feature=share
# https://github.com/fnneves/portfolio_tracker_medium

# Callback Dash: https://www.youtube.com/watch?v=uzosQuETMKo

# Bootstraps Components: https://dash-bootstrap-components.opensource.faculty.ai/
# Bootstraps Themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
# Bootstraps App Gallery: https://hellodash.pythonanywhere.com/app_gallery

# https://plotly.com/python/indicator/
# https://plotly.com/python/reference/indicator/


# https://plotly.com/python/time-series/

# editable table: https://dash.plotly.com/datatable/editable

# -------------------------------------------------------------------------------------------
#                                       *** LIBRARIES ***
# -------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import time
import datetime
from datetime import date, datetime, timezone

#import ipdb # --> per Debug CallBacks

# CoinGecko
from pycoingecko import CoinGeckoAPI

# Yahoo Finance
import yfinance as yf

# Dash
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dash_table
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template
from dash import dash_table as dt
import plotly.express as px
import plotly.figure_factory as ff

# import dash_core_components as dcc
# Multipage
from app import app

# -------------------------------------------------------------------------------------------
#                                       *** DATA ***
# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------
# Get Data from CoinGeko
# -------------------------------------------------------------------------------------------
cg = CoinGeckoAPI()
MarketData = cg.get_coins_markets(vs_currency='usd', per_page=100, page=1)
MarketData = pd.DataFrame(MarketData)
# print(MarketData)
#ipdb.set_trace()
MarketData['Circulating Supply %'] = MarketData['circulating_supply'] / MarketData['total_supply']
# MarketData[['Circulating Supply %']] = MarketData[['Circulating Supply %']]. fillna('')
MarketData['symbol'] = MarketData['symbol'].str.upper()
MarketData['market_cap'] = MarketData['market_cap'] / 10 ** 9
# print(MarketData.columns)

# MarketData.set_index('market_cap_rank', inplace=True)
MarketData.drop(['image', 'fully_diluted_valuation', 'total_volume', 'high_24h', 'low_24h', 'price_change_24h',
                 'market_cap_change_24h', 'market_cap_change_percentage_24h', 'max_supply', 'atl',
                 'atl_change_percentage', 'atl_date', 'roi', 'last_updated', 'ath_date', 'circulating_supply',
                 'total_supply'], axis=1, inplace=True)
MarketData = MarketData[
    ['market_cap_rank', 'id', 'name', 'symbol', 'current_price', 'price_change_percentage_24h', 'ath',
     'ath_change_percentage', 'market_cap', 'Circulating Supply %']]
MarketData.rename(columns={'market_cap_rank': 'Rank',
                           'name': 'Currency',
                           'symbol': 'Symbol',
                           'current_price': 'Price (USD)',
                           'price_change_percentage_24h': 'Change 24H (%)',
                           'ath': 'ATH (USD)',
                           'ath_change_percentage': 'ATH Change (%)',
                           'market_cap': 'Market Cap (USDm)'
                           }, inplace=True)

MarketData = MarketData.round(
    {'Change 24H (%)': 2, 'Circulating Supply %': 4, 'ATH Change (%)': 2, 'Market Cap (USDm)': 2})

# Vector for P.lio Weight (dropdown)
PercentageV = np.linspace(0, 1, 21)
PercentageV = pd.DataFrame(PercentageV)
PercentageV['id'] = PercentageV[0]
PercentageV[0] = PercentageV[0].astype(float).map("{:.0%}".format)

# -------------------------------------------------------------------------------------------
#                                       *** DASH APP ***
# -------------------------------------------------------------------------------------------
# Style
load_figure_template('darkly')
HeightIndicators = 70
FontSize = 13
HeightDiv = '35px'
MarginBDiv = 7
PaddingTopDiv = 8
HeightDrop = '25px'
MarginBDrop = 17



layout = dbc.Container(
    [
        html.P(),
        html.P(),
        html.Hr(),

        # Header
        dbc.Row(dbc.Col(html.H5('CRYPTO PORTFOLIO ANALYSIS', className='text-center', style={'color': '#3498DB'}))),
        # text-primary, mb-3'))), # header row

        html.Hr(),

        # First row
        # html.P('Google Trends for Gold, Bitcoin and Ethereum', className='text-center'),
        dbc.Row([
            dbc.Col([
                html.Div('Capital Invested (USD):', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                dbc.Input(id='CapitalInvestedInput', placeholder='CapitalInvestedInput', value=10000, type="number",
                          style={'backgroundColor': 'white', 'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize}),
            ], width={'size': 2, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),

        dbc.Row([
            dbc.Col([
                html.Div('Crypto', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Last Price (USD)', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div('Weight', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div('Quantity', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 4}),
            dbc.Col([
                html.Div('Investment (USD)', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='Crypto1',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='bitcoin',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Crypto2',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='ethereum',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Crypto3',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='binancecoin',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Crypto4',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='cardano',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Crypto5',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='solana',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dbc.Button('>> Run Chart <<',
                           id='Run_Chart_Plio',
                           color='info',
                           size='sm',
                           className="d-grid gap-2 mx-auto",
                           n_clicks=0),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div(id='Crypto1Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto2Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto3Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto4Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto5Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 2}),
            dbc.Col([
                dcc.Dropdown(id='Weight1',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Weight2',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Weight3',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Weight4',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Weight5',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                html.Div(id='WeightTot', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div(id='Crypto1Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto2Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto3Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto4Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto5Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 4}),
            dbc.Col([
                html.Div(id='Invest1Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest2Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest3Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest4Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest5Qty', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        # -------------------------------------------------------------------------------------------
        # CHARTS
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row([
            dbc.Col([
                # html.P('Price (USD)', className='text-center'),
                dcc.Graph(id='CryptoVolRet',
                          style={'height': 350},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 6, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='CryptoHistory',
                          style={'height': 350},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 6, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),

        # -------------------------------------------------------------------------------------------
        # STATISTICS
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div('Asset', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Annualized Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div('Annualized Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div('Sharpe Ratio', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 4}),
            dbc.Col([
                html.Div('Correlation Matrix', className='text-center',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 4, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        dbc.Row([
            dbc.Col([
                html.Div(id='Crypto1Sym', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto2Sym', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto3Sym', className='text-leftr',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto4Sym', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto5Sym', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div('PORTFOLIO', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),

            dbc.Col([
                html.Div(id='Crypto1Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto2Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto3Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto4Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto5Return', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='PlioReturn', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div(id='Crypto1Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto2Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto3Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto4Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Crypto5Volatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='PlioVolatility', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div(id='Invest1SharpeR', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest2SharpeR', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest3SharpeR', className='text-leftr',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest4SharpeR', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='Invest5SharpeR', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='PlioSharpeR', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 4}),
            dbc.Col([
                # html.P('Price (USD)', className='text-center'),
                dcc.Graph(id='CryptoCorrelation',
                          style={'height': 300},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        # -------------------------------------------------------------------------------------------
        # FORECAST
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row(dbc.Col(html.H5('PORTFOLIO FORECAST ANALYSIS', className='text-center', style={'color': '#3498DB'}))),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.Div('Portfolio setting', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div('Period Forward', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div('Market view 1', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div('Market view 2', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div('Target loss', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),

            dbc.Col([
                html.Div(id='xx', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                dcc.Dropdown(id='PeriodForward',
                             options=[
                                 {'label': '1 Month', 'value': 31},
                                 {'label': '3 Months', 'value': 92},
                                 {'label': '6 Months', 'value': 182},
                                 {'label': '1 Year', 'value': 366},
                             ],
                             value=31,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='MarketView1',
                             options=[
                                 {'label': 'Steady', 'value': 2},
                                 {'label': 'Bull', 'value': 1},
                                 {'label': 'Bear', 'value': 3},
                             ],
                             value=2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='MarketView2',
                             options=[
                                 {'label': 'Steady', 'value': 2},
                                 {'label': 'Bull', 'value': 1},
                                 {'label': 'Bear', 'value': 3},
                             ],
                             value=2,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='LossPrice',
                             options=[
                                 {'label': PercentageV[0][k], 'value': PercentageV['id'][k]} for k in
                                 range(len(PercentageV))
                             ],
                             value=.1,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dbc.Button('>> Run Chart <<',
                           id='Run_Chart2',
                           color='info',
                           size='sm',
                           className="d-grid gap-2 mx-auto",
                           n_clicks=0),
            ], width={'size': 2, 'offset': 0, 'order': 2}),

            dbc.Col([
                dcc.Graph(id='PlioForecast',
                          style={'height': 250},
                          config={"displayModeBar": False, "showTips": False}),
                html.Hr(),
                dcc.Graph(id='PlioPercentage',
                          style={'height': 150},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 8, 'offset': 0, 'order': 3}),
        ], className="mx-3",
        ),


        # -------------------------------------------------------------------------------------------
        # CLOSING
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div('The Website provides analysis of the Crypto market.'
                         ' In addition to tracking price, volume and market capitalisation, it provides in deep analysis and statistics of single Crypto or as a Portfolio of Crypto',
                         className='text-left',
                         style={'height': 130, 'marginBottom': MarginBDiv, 'fontSize': FontSize - 1,
                                'paddingTop': PaddingTopDiv}),
                html.Div('© 2022 - All Rights Reserved',
                         className='text-left',
                         style={'color': '#cccccc', 'height': '20px', 'marginBottom': 0,
                                'fontSize': FontSize - 1,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 3, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Contacts: xxx@xxx.ai',
                         className='text-left',
                         style={'color': '#cccccc', 'height': '20px', 'marginBottom': 0, 'fontSize': FontSize - 1,
                                'paddingTop': PaddingTopDiv}),
                html.Div('Market Data from: coingecko.com',
                         className='text-left',
                         style={'color': '#cccccc', 'height': '20px', 'marginBottom': 50,
                                'fontSize': FontSize - 1,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 3, 'offset': 0, 'order': 2}),
        ], className="mx-5",
        ),
        html.P(),

    ], fluid=True)


# -------------------------------------------------------------------------------------------
# Get Data from CoinGecko - PRICE, VOLUME, MARKET CAP
# -------------------------------------------------------------------------------------------

#https://dash.plotly.com/basic-callbacks
@app.callback(Output(component_id='Crypto1Price', component_property='children'),
              Output(component_id='Crypto2Price', component_property='children'),
              Output(component_id='Crypto3Price', component_property='children'),
              Output(component_id='Crypto4Price', component_property='children'),
              Output(component_id='Crypto5Price', component_property='children'),
              Output(component_id='WeightTot', component_property='children'),
              Output(component_id='Crypto1Qty', component_property='children'),
              Output(component_id='Crypto2Qty', component_property='children'),
              Output(component_id='Crypto3Qty', component_property='children'),
              Output(component_id='Crypto4Qty', component_property='children'),
              Output(component_id='Crypto5Qty', component_property='children'),
              Output(component_id='Invest1Qty', component_property='children'),
              Output(component_id='Invest2Qty', component_property='children'),
              Output(component_id='Invest3Qty', component_property='children'),
              Output(component_id='Invest4Qty', component_property='children'),
              Output(component_id='Invest5Qty', component_property='children'),
              Output(component_id='CryptoVolRet', component_property='figure'),
              Output(component_id='CryptoHistory', component_property='figure'),
              Output(component_id='Crypto1Sym', component_property='children'),
              Output(component_id='Crypto2Sym', component_property='children'),
              Output(component_id='Crypto3Sym', component_property='children'),
              Output(component_id='Crypto4Sym', component_property='children'),
              Output(component_id='Crypto5Sym', component_property='children'),
              Output(component_id='Crypto1Return', component_property='children'),
              Output(component_id='Crypto2Return', component_property='children'),
              Output(component_id='Crypto3Return', component_property='children'),
              Output(component_id='Crypto4Return', component_property='children'),
              Output(component_id='Crypto5Return', component_property='children'),
              Output(component_id='PlioReturn', component_property='children'),
              Output(component_id='Crypto1Volatility', component_property='children'),
              Output(component_id='Crypto2Volatility', component_property='children'),
              Output(component_id='Crypto3Volatility', component_property='children'),
              Output(component_id='Crypto4Volatility', component_property='children'),
              Output(component_id='Crypto5Volatility', component_property='children'),
              Output(component_id='PlioVolatility', component_property='children'),
              #Output(component_id='DailyPlioVolatility', component_property='children'),
              Output(component_id='Invest1SharpeR', component_property='children'),
              Output(component_id='Invest2SharpeR', component_property='children'),
              Output(component_id='Invest3SharpeR', component_property='children'),
              Output(component_id='Invest4SharpeR', component_property='children'),
              Output(component_id='Invest5SharpeR', component_property='children'),
              Output(component_id='PlioSharpeR', component_property='children'),
              Output(component_id='CryptoCorrelation', component_property='figure'),
              State(component_id='CapitalInvestedInput', component_property='value'),
              State(component_id='Crypto1', component_property='value'),
              State(component_id='Crypto2', component_property='value'),
              State(component_id='Crypto3', component_property='value'),
              State(component_id='Crypto4', component_property='value'),
              State(component_id='Crypto5', component_property='value'),
              State(component_id='Weight1', component_property='value'),
              State(component_id='Weight2', component_property='value'),
              State(component_id='Weight3', component_property='value'),
              State(component_id='Weight4', component_property='value'),
              State(component_id='Weight5', component_property='value'),
              [
               #Input(component_id='CapitalInvestedInput', component_property='value'),
               #Input(component_id='Crypto1', component_property='value'),
               #Input(component_id='Crypto2', component_property='value'),
               #Input(component_id='Crypto3', component_property='value'),
               #Input(component_id='Crypto4', component_property='value'),
               #Input(component_id='Crypto5', component_property='value'),
               #Input(component_id='Weight1', component_property='value'),
               #Input(component_id='Weight2', component_property='value'),
               #Input(component_id='Weight3', component_property='value'),
               #Input(component_id='Weight4', component_property='value'),
               #Input(component_id='Weight5', component_property='value'),
               Input('Run_Chart_Plio', 'n_clicks')
               ]
              )

def Portfolio1(CapitalInvestedInput,
               Crypto1, Crypto2, Crypto3, Crypto4, Crypto5,
               Weight1, Weight2, Weight3, Weight4, Weight5,
               n):

    File_In_Name = '2021.12.24_CoinGeko_List_Symbol.xlsx'
    Sheet_Name_In = 'DataSet'
    CryptoSymbolDf = pd.read_excel(File_In_Name, sheet_name=Sheet_Name_In, engine='openpyxl')

    DDCoingecko = 366

    # Input
    CryptoList = [''] * 5
    CryptoList[0] = Crypto1
    CryptoList[1] = Crypto2
    CryptoList[2] = Crypto3
    CryptoList[3] = Crypto4
    CryptoList[4] = Crypto5

    CryptoWeight = [''] * 5
    CryptoWeight[0] = Weight1
    CryptoWeight[1] = Weight2
    CryptoWeight[2] = Weight3
    CryptoWeight[3] = Weight4
    CryptoWeight[4] = Weight5

    # Symbols
    Crypto1Sym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[0])]['symbolCapital'].values[0]
    Crypto2Sym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[1])]['symbolCapital'].values[0]
    Crypto3Sym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[2])]['symbolCapital'].values[0]
    Crypto4Sym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[3])]['symbolCapital'].values[0]
    Crypto5Sym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[4])]['symbolCapital'].values[0]

    # Run
    for i in range(5):
        HistoryPriceCrypto = cg.get_coin_market_chart_by_id(id=CryptoList[i], vs_currency='usd', interval='daily', days=str(DDCoingecko))
        HistoryPriceCrypto = pd.DataFrame(HistoryPriceCrypto['prices'])
        HistoryPriceCrypto.columns = ['Date', CryptoList[i]]
        HistoryPriceCrypto['Date'] = pd.to_datetime(HistoryPriceCrypto['Date'], unit='ms')
        HistoryPriceCrypto['Date'] = pd.to_datetime(HistoryPriceCrypto['Date']).dt.date
        HistoryPriceCrypto.drop([len(HistoryPriceCrypto) - 2], inplace=True)

        if i == 0:
            MatrixPriceCrypto = HistoryPriceCrypto.copy(deep=True)

        else:
            MatrixPriceCrypto = MatrixPriceCrypto.join(HistoryPriceCrypto.set_index('Date'), on='Date')

        # time.sleep(5)

    MatrixPriceCrypto = MatrixPriceCrypto.fillna(method='pad')
    MatrixPriceCrypto = MatrixPriceCrypto.fillna(method='bfill')

    # Price Output
    PlioMatrix = pd.DataFrame()
    PlioMatrix['Last Price'] = MatrixPriceCrypto.iloc[- 1, -5:].T
    PlioMatrix['Capital'] = CapitalInvestedInput
    PlioMatrix['Weight'] = CryptoWeight
    PlioMatrix['Invested'] = PlioMatrix['Capital'] * PlioMatrix['Weight']
    PlioMatrix['Quantity'] = PlioMatrix['Invested'] / PlioMatrix['Last Price']
    PlioMatrix = PlioMatrix.round(2)

    # Weight Tot
    SumMatrix = PlioMatrix.sum()
    WeightTot = '{:.0%}'.format(SumMatrix['Weight'])

    # Price Output
    LastPrice = MatrixPriceCrypto.iloc[-1:]
    LastPrice = LastPrice.drop(columns=['Date'])

    for i in CryptoList:
        LastPrice.loc[LastPrice[i] > 1, i] = np.round(LastPrice[i], 2)
        LastPrice.loc[LastPrice[i] <= 1, i] = np.round(LastPrice[i], 6)

    LastPrice1 = '{:,f}'.format(LastPrice.iloc[0][CryptoList[0]])
    LastPrice2 = '{:,f}'.format(LastPrice.iloc[0][CryptoList[1]])
    LastPrice3 = '{:,f}'.format(LastPrice.iloc[0][CryptoList[2]])
    LastPrice4 = '{:,f}'.format(LastPrice.iloc[0][CryptoList[3]])
    LastPrice5 = '{:,f}'.format(LastPrice.iloc[0][CryptoList[4]])

    # Q.ty Output
    Crypto1Qty = '{:,.2f}'.format(PlioMatrix['Quantity'][0]) + ' ' + CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[0])]['symbolCapital'].values[0]
    Crypto2Qty = '{:,.2f}'.format(PlioMatrix['Quantity'][1]) + ' ' + CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[1])]['symbolCapital'].values[0]
    Crypto3Qty = '{:,.2f}'.format(PlioMatrix['Quantity'][2]) + ' ' + CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[2])]['symbolCapital'].values[0]
    Crypto4Qty = '{:,.2f}'.format(PlioMatrix['Quantity'][3]) + ' ' + CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[3])]['symbolCapital'].values[0]
    Crypto5Qty = '{:,.2f}'.format(PlioMatrix['Quantity'][4]) + ' ' + CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == CryptoList[4])]['symbolCapital'].values[0]

    # Invested Output
    Invest1Qty = '{:,.2f}'.format(PlioMatrix['Invested'][0])
    Invest2Qty = '{:,.2f}'.format(PlioMatrix['Invested'][1])
    Invest3Qty = '{:,.2f}'.format(PlioMatrix['Invested'][2])
    Invest4Qty = '{:,.2f}'.format(PlioMatrix['Invested'][3])
    Invest5Qty = '{:,.2f}'.format(PlioMatrix['Invested'][4])

    # -----------------------------------------------------------------------
    # Chart
    # Columns returns and statistic
    MatrixReturnCrypto = MatrixPriceCrypto.copy(deep=True)
    MatrixReturnCrypto = MatrixReturnCrypto.drop(columns=['Date'])
    MatrixReturnCrypto = MatrixReturnCrypto.pct_change()
    VarCovMatrix = MatrixReturnCrypto.cov()
    CorrMatrix = MatrixReturnCrypto.corr()

    for i in range(len(CryptoList)):
        MatrixReturnCrypto['Weighted_Ret ' + CryptoList[i]] = MatrixReturnCrypto[CryptoList[i]] * CryptoWeight[i]

    MatrixReturnCrypto['PlioRet'] = MatrixReturnCrypto['Weighted_Ret ' + CryptoList[0]] + \
                                    MatrixReturnCrypto['Weighted_Ret ' + CryptoList[1]] + \
                                    MatrixReturnCrypto['Weighted_Ret ' + CryptoList[2]] + \
                                    MatrixReturnCrypto['Weighted_Ret ' + CryptoList[3]] + \
                                    MatrixReturnCrypto['Weighted_Ret ' + CryptoList[4]]

    MatrixReturnCrypto['PlioRet_CumSum'] = MatrixReturnCrypto['PlioRet'].cumsum()
    MatrixReturnCrypto['Plio'] = CapitalInvestedInput * (1 + MatrixReturnCrypto['PlioRet_CumSum'])
    MatrixReturnCrypto['Plio'] = MatrixReturnCrypto['Plio'].fillna(CapitalInvestedInput)

    VectorReturns = MatrixReturnCrypto.mean() * 365
    VectorReturns = pd.DataFrame(VectorReturns)
    VectorStDev = MatrixReturnCrypto.std() * np.sqrt(365)
    VectorStDev = pd.DataFrame(VectorStDev)

    # -------------------------------------------------------------------------------------------
    # CHART 1 & 2
    # -------------------------------------------------------------------------------------------

    # Add Data Column
    FirstDate = MatrixPriceCrypto.iloc[0]['Date']
    MatrixReturnCrypto['Date'] = pd.date_range(start=FirstDate, periods=len(MatrixPriceCrypto), freq='D')

    # Scatter volatility - returns
    # https://plotly.com/python/text-and-annotations/
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[0, 0]], y=[VectorReturns.iloc[0, 0]], text=[Crypto1Sym], name=CryptoList[0],
                   mode='markers+text', marker=dict(size=10, color='blue')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[1, 0]], y=[VectorReturns.iloc[1, 0]], text=[Crypto2Sym], name=CryptoList[1],
                   mode='markers+text', marker=dict(size=10, color='blue')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[2, 0]], y=[VectorReturns.iloc[2, 0]], text=[Crypto3Sym], name=CryptoList[2],
                   mode='markers+text', marker=dict(size=10, color='blue')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[3, 0]], y=[VectorReturns.iloc[3, 0]], text=[Crypto4Sym], name=CryptoList[3],
                   mode='markers+text', marker=dict(size=10, color='blue')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[4, 0]], y=[VectorReturns.iloc[4, 0]], text=[Crypto5Sym], name=CryptoList[4],
                   mode='markers+text', marker=dict(size=10, color='blue')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[10, 0]], y=[VectorReturns.iloc[10, 0]], text=['Portfolio'], name='Portfolio',
                   mode='markers+text', marker=dict(size=10, color='#3498db')))

    # lines
    fig1.add_trace(
        go.Scatter(x=[0, VectorStDev.iloc[10, 0]], y=[VectorReturns.iloc[10, 0], VectorReturns.iloc[10, 0]],
                   mode='lines', line=dict(width=1, dash='dot', color='#3498db')))
    fig1.add_trace(
        go.Scatter(x=[VectorStDev.iloc[10, 0], VectorStDev.iloc[10, 0]], y=[0, VectorReturns.iloc[10, 0]], mode='lines',
                   line=dict(width=1, dash='dot', color='#3498db')))

    # Layout
    fig1.update_layout(title='Portfolio Risk - Performance vs. Crypto', font=dict(size=10))
    fig1.update_layout(xaxis_title='Annualized Volatility (Risk)', yaxis_title='Annualized Return',
                       yaxis_tickformat='.0%', xaxis_tickformat='.0%')
    fig1.update_traces(textposition='top center', textfont_size=11) #top/bottom
    #fig1.update_layout(yaxis_type="log", xaxis_type="log")

    fig1.update_layout(margin=dict(l=20, r=0, t=25, b=10), paper_bgcolor="#222222")
    fig1.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})
    fig1.update_layout(showlegend=False)
    # fig1.show()

    # Line chart
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(x=MatrixReturnCrypto['Date'], y=MatrixReturnCrypto['Plio'], mode='lines', name='Portfolio',
                   line=dict(width=1, color='#3498db')))
    fig2.update_layout(title='Portfolio Performance over the period (Backtest)', font=dict(size=10))
    fig2.update_layout(xaxis_title='Period', yaxis_title='Portfolio Growth')
    # fig2.update_traces(textposition='top center')
    # fig2.update_layout(yaxis_type="log", xaxis_type="log")
    fig2.update_layout(margin=dict(l=20, r=0, t=25, b=10), paper_bgcolor="#222222")
    fig2.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})
    # fig2.update_layout(showlegend=False)
    #fig2.show()

    # -------------------------------------------------------------------------------------------
    # OUTPUT & CORRELATION MATRIX
    # -------------------------------------------------------------------------------------------

    # OUTPUT
    # Return
    Crypto1Return = '{:.2%}'.format(VectorReturns.iloc[0, 0]).replace('%', ' %')
    Crypto2Return = '{:.2%}'.format(VectorReturns.iloc[1, 0]).replace('%', ' %')
    Crypto3Return = '{:.2%}'.format(VectorReturns.iloc[2, 0]).replace('%', ' %')
    Crypto4Return = '{:.2%}'.format(VectorReturns.iloc[3, 0]).replace('%', ' %')
    Crypto5Return = '{:.2%}'.format(VectorReturns.iloc[4, 0]).replace('%', ' %')
    PlioReturn = '{:.2%}'.format(VectorReturns.iloc[10, 0]).replace('%', ' %')

    # Volatitlity
    Crypto1Volatility = '{:.2%}'.format(VectorStDev.iloc[0, 0]).replace('%', ' %')
    Crypto2Volatility = '{:.2%}'.format(VectorStDev.iloc[1, 0]).replace('%', ' %')
    Crypto3Volatility = '{:.2%}'.format(VectorStDev.iloc[2, 0]).replace('%', ' %')
    Crypto4Volatility = '{:.2%}'.format(VectorStDev.iloc[3, 0]).replace('%', ' %')
    Crypto5Volatility = '{:.2%}'.format(VectorStDev.iloc[4, 0]).replace('%', ' %')
    PlioVolatility = '{:.2%}'.format(VectorStDev.iloc[10, 0]).replace('%', ' %')
    #DailyPlioVolatility = VectorStDev.iloc[10, 0]

    # Sharpe Ratio
    Invest1SharpeR = '{:.2}'.format(VectorReturns.iloc[0, 0] / VectorStDev.iloc[0, 0])
    Invest2SharpeR = '{:.2}'.format(VectorReturns.iloc[1, 0] / VectorStDev.iloc[1, 0])
    Invest3SharpeR = '{:.2}'.format(VectorReturns.iloc[2, 0] / VectorStDev.iloc[2, 0])
    Invest4SharpeR = '{:.2}'.format(VectorReturns.iloc[3, 0] / VectorStDev.iloc[3, 0])
    Invest5SharpeR = '{:.2}'.format(VectorReturns.iloc[4, 0] / VectorStDev.iloc[4, 0])
    PlioSharpeR = '{:.2}'.format(VectorReturns.iloc[10, 0] / VectorStDev.iloc[10, 0])

    # Set Symbol to Correlation Matrix
    CorrMatrix = CorrMatrix.rename(columns={CryptoList[0]: Crypto1Sym,
                                            CryptoList[1]: Crypto2Sym,
                                            CryptoList[2]: Crypto3Sym,
                                            CryptoList[3]: Crypto4Sym,
                                            CryptoList[4]: Crypto5Sym})

    CorrMatrix = CorrMatrix.rename(index={CryptoList[0]: Crypto1Sym,
                                          CryptoList[1]: Crypto2Sym,
                                          CryptoList[2]: Crypto3Sym,
                                          CryptoList[3]: Crypto4Sym,
                                          CryptoList[4]: Crypto5Sym})

    # Correlation Matrix
    fig3 = px.imshow(CorrMatrix,
                    color_continuous_scale="blues",
                    color_continuous_midpoint=0,
                    labels=dict(color='Correlation'),
                    #text_auto='.2f',
                    zmin=-1, zmax=1,
                    )
    fig3.update_xaxes(side="top")
    fig3.update_coloraxes(showscale=False)
    fig3.update_layout(margin=dict(l=20, r=0, t=25, b=10), paper_bgcolor="#222222")

    # FUNCTION OUTPUTS
    return LastPrice1, LastPrice2, LastPrice3, LastPrice4, LastPrice5, WeightTot, \
           Crypto1Qty, Crypto2Qty, Crypto3Qty, Crypto4Qty, Crypto5Qty, \
           Invest1Qty, Invest2Qty, Invest3Qty, Invest4Qty, Invest5Qty, \
           fig1, fig2, \
           Crypto1Sym, Crypto2Sym, Crypto3Sym, Crypto4Sym, Crypto5Sym, \
           Crypto1Return, Crypto2Return, Crypto3Return, Crypto4Return, Crypto5Return, PlioReturn, \
           Crypto1Volatility, Crypto2Volatility, Crypto3Volatility, Crypto4Volatility, Crypto5Volatility, PlioVolatility, \
           Invest1SharpeR, Invest2SharpeR, Invest3SharpeR, Invest4SharpeR, Invest5SharpeR, PlioSharpeR, \
           fig3

    # -------------------------------------------------------------------------------------------
    # FORECAST
    # -------------------------------------------------------------------------------------------
@app.callback(#Output(component_id='CryptoNameSymbol', component_property='children'),
              Output(component_id='PlioForecast', component_property='figure'),
              Output(component_id='PlioPercentage', component_property='figure'),
              State(component_id='PeriodForward', component_property='value'),
              State(component_id='MarketView1', component_property='value'),
              State(component_id='MarketView2', component_property='value'),
              State('LossPrice', 'value'),
             [Input(component_id='CapitalInvestedInput', component_property='value'),
              Input(component_id='PlioVolatility', component_property='children'),
              Input('Run_Chart2', 'n_clicks')],
              )

def ForecastAnalysis(PeriodForward,
                     MarketView1,
                     MarketView2,
                     LossPrice,
                     CapitalInvestedInput,
                     PlioVolatility,
                     n,
                     ):

    '''
    File_In_Name = '2021.12.24_CoinGeko_List_Symbol.xlsx'
    Sheet_Name_In = 'DataSet'
    CryptoSymbolDf = pd.read_excel(File_In_Name, sheet_name=Sheet_Name_In, engine='openpyxl')

    CryptoName = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['name'].values[0]
    CryptoSym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['symbolCapital'].values[0]
    CryptoNameSymbol = CryptoName + ' (' + CryptoSym + ')'
    '''

    #Period = 365
    Np = 100
    T = PeriodForward
    Dt = 1
    Nmu = 0
    Nsigma = 1

    SelectTrend1 = MarketView1  # bull, flat, bear
    SelectTrend2 = MarketView2  # bull, flat, bear

    DevStd = float(str(PlioVolatility[:-2])) / 100 / np.sqrt(365)

    # Def Trend 1
    if SelectTrend1 == 1:
        Mu1 = 1/365
    elif SelectTrend1 == 2:
        Mu1 = 0
    elif SelectTrend1 == 3:
        Mu1 = .5/365

    # Def Trend 2
    if SelectTrend2 == 1:
        Mu2 = 1/365
    elif SelectTrend2 == 2:
        Mu2 = 0
    elif SelectTrend2 == 3:
        Mu2 = .5/365

    # GBM
    GBMmatrix = np.zeros((Np, T))
    GBMmatrix[:, 0] = CapitalInvestedInput

    # >> usato rendimento e volatilità giornalieri e Dt = 1
    for j in range(0, Np):
        for i in range(1, T):
            if i <= int(T / 2):
                Mu = Mu1
            else:
                Mu = Mu2

            GBMmatrix[j, i] = GBMmatrix[j, i - 1] * np.exp(
                (Mu - (DevStd ** 2) / 2) * Dt + DevStd * np.random.normal(Nmu, Nsigma) * np.sqrt(Dt))

    GBMmatrix = pd.DataFrame(GBMmatrix)

    # Gouge propability Price >= Strike

    Strike = CapitalInvestedInput * (1 - LossPrice)
    GBMmatrixPerc = GBMmatrix.copy()
    GBMmatrixPerc = GBMmatrixPerc - Strike
    GBMmatrixPerc[GBMmatrixPerc >= 0] = 0
    GBMmatrixPerc[GBMmatrixPerc < 0] = 1

    V_sum = pd.DataFrame(GBMmatrixPerc.sum()) / len(GBMmatrixPerc)
    V_sum = V_sum.reset_index()
    LastDate = pd.to_datetime("today")
    V_sum['index1'] = pd.date_range(start=LastDate, periods=T, freq='D')

    # Matrix for Area chart
    Plot_Matrix = pd.DataFrame()
    Plot_Matrix['index1'] = pd.date_range(start=LastDate, periods=T, freq='D')
    Plot_Matrix['Min'] = GBMmatrix.quantile(.05)  # pd.DataFrame(GBMmatrix.min())
    Plot_Matrix['Max'] = GBMmatrix.quantile(.95)  # pd.DataFrame(GBMmatrix.max())
    Plot_Matrix['Average Price'] = pd.DataFrame(GBMmatrix.mean())
    Plot_Matrix['Price Q1'] = GBMmatrix.quantile(.1)
    # Plot_Matrix['Price Q2'] = GBMmatrix.quantile(.2)
    Plot_Matrix['Price Q3'] = GBMmatrix.quantile(.3)
    Plot_Matrix['Price Q4'] = GBMmatrix.quantile(.7)
    # Plot_Matrix['Price Q5'] = GBMmatrix.quantile(.8)
    Plot_Matrix['Price Q6'] = GBMmatrix.quantile(.9)
    #Plot_Matrix['Strike'] = Strike
    Plot_Matrix['Ones'] = 1

    # Chart Area
    # https://plotly.com/python/filled-area-plots/
    fig5 = go.Figure()
    #fig5.add_trace(
        #go.Scatter(x=PriceHistC['Date'], y=PriceHistC['Price'], name='Historical Price', fill='none', mode='lines',
                   #line=dict(width=1, color='#3498db')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Min'], name='', fill='none', mode='lines',
                   line=dict(width=0, color='black')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q1'], name='Worst 10% chance', fill='tonexty',
                   mode='lines', line=dict(width=0, color='red')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q3'], name='20% chance', fill='tonexty',
                   mode='lines',
                   line=dict(width=0, color='orange')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q4'], name='40% chance - Most Likely',
                   fill='tonexty', mode='lines',
                   line=dict(width=0, color='yellow')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q6'], name='20% chance', fill='tonexty',
                   mode='lines',
                   line=dict(width=0, color='yellowgreen')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Max'], name='Best 10% chance', fill='tonexty',
                   mode='lines',
                   line=dict(width=0, color='lightgreen')))

    fig5.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1, font=(dict(size=9.5))))
    fig5.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222")
    fig5.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    # probability
    fig6 = go.Figure()
    fig6.add_trace(
        go.Scatter(x=V_sum['index1'], y=V_sum[0], name='Portfolio lost probability of ' + '{:,.0%}'.format(LossPrice) + ' over the period',
                   fill='tonexty',
                   mode='lines', line=dict(width=1, color='#3498db')))
    fig6.add_trace(go.Scatter(x=Plot_Matrix['index1'], name='', y=Plot_Matrix['Ones'], fill='none', mode='none'))

    fig6.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))
    fig6.update_layout(yaxis_tickformat='.2%')
    fig6.update_layout(margin=dict(l=50, t=10),
                       paper_bgcolor="#222222")  # https://plotly.com/python/setting-graph-size/#adjusting-height-width--margins
    fig6.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    return fig5, fig6

# -------------------------------------------------------------------------------------------
#                                         --- END ---
# -------------------------------------------------------------------------------------------