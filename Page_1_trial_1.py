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
        dbc.Row(dbc.Col(html.H5('CRYPTO ANALYSIS', className='text-center', style={'color': '#3498DB'}))),
        # text-primary, mb-3'))), # header row

        html.Hr(),
        html.P(),
        html.P(),

        # First row
        # html.P('Google Trends for Gold, Bitcoin and Ethereum', className='text-center'),

        dbc.Row([
            dbc.Col([
                html.Div('Select Crypto', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Price (USD)', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 1, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div('1D', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 1, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div('1W', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 1, 'offset': 0, 'order': 4}),
            dbc.Col([
                html.Div('YTD', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 1, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='DropdownListCrypto1',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='bitcoin',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop + 10,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
            ], width={'size': 2, 'offset': 0, 'order': 1}),

            dbc.Col([
                html.Div(id='LastPrice', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv})
            ], width={'size': 1, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div(id='DayPerc', className='text-center',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv})
            ], width={'size': 1, 'offset': 0, 'order': 3}),
            dbc.Col([
                html.Div(id='WeekPerc', className='text-center',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv})
            ], width={'size': 1, 'offset': 0, 'order': 4}),
            dbc.Col([
                html.Div(id='YTDPerc', className='text-center',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv})
            ], width={'size': 1, 'offset': 0, 'order': 5}),
        ], className="mx-3",
        ),

        # Charts Price, Volumes, Market Cap
        dbc.Row([
            dbc.Col([
                html.Div('Price (USD)', className='text-center', style={'height': HeightDiv, 'marginBottom': 0, 'fontSize': FontSize}),
                dcc.Graph(id='CryptoPrice',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Volumes (USD)', className='text-center', style={'height': HeightDiv, 'marginBottom': 0, 'fontSize': FontSize}),
                dcc.Graph(id='CryptoVolume',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div('Market Cap (USD)', className='text-center', style={'height': HeightDiv, 'marginBottom': 0, 'fontSize': FontSize}),
                dcc.Graph(id='CryptoMarketCap',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 3}),
        ], className="mx-3",
        ),

        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.Div('Capital', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Benchmark 1', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Benchmark 2', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Period', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Rolling Days', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Statistics', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),

            dbc.Col([
                dbc.Input(id='CapitalInvest', placeholder='CapitalInvest', value=1000, type="number",
                          style={'backgroundColor': 'white', 'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize}),
                dcc.Dropdown(id='DropdownListBenchmark1',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='tether',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='DropdownListBenchmark2',
                             options=[
                                 {'label': MarketData['Currency'][k], 'value': MarketData['id'][k]} for k in
                                 range(len(MarketData))
                             ],
                             value='usd-coin',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='DropdownPeriod',
                             options=[
                                 {'label': '1 Year', 'value': '365'},
                                 {'label': '1 Month', 'value': '31'},
                                 {'label': '3 Months', 'value': '91'},
                                 {'label': '6 Months', 'value': '181'},
                                 {'label': 'YTD', 'value': 'ytd'},
                             ],
                             value='ytd',
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='DropdownRolling',
                             options=[
                                 {'label': '15 days', 'value': 15},
                                 {'label': '30 days', 'value': 30},
                                 {'label': '60 days', 'value': 60},
                                 {'label': '90 days', 'value': 90},
                             ],
                             value=30,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dcc.Dropdown(id='Statistics1',
                             options=[
                                 {'label': 'Volatility', 'value': 1},
                                 {'label': 'Correlation', 'value': 2},
                                 {'label': 'Sharpe Ratio', 'value': 3},
                             ],
                             value=1,
                             style={
                                 'color': '#000000',
                                 'background-clip': '#11b9bf',
                                 'marginBottom': MarginBDrop,
                                 'height': HeightDrop,
                                 'fontSize': FontSize,
                             }),
                dbc.Button('>> Run Chart <<',
                           id='Run_Chart1',
                           color='info',
                           size='sm',
                           className="d-grid gap-2 mx-auto",
                           n_clicks=0),
            ], width={'size': 2, 'offset': 0, 'order': 2}),

            dbc.Col([
                # html.P('Price (USD)', className='text-center'),
                dcc.Graph(id='CryptoBenchmark',
                          style={'height': 250},
                          config={"displayModeBar": False, "showTips": False}),
                html.Hr(),
                dcc.Graph(id='CryptoStatistics',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 8, 'offset': 0, 'order': 3}),

        ], className="mx-3",
        ),

        # -------------------------------------------------------------------------------------------
        # FORECAST
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row(dbc.Col(html.H5('CRYPTO FORECAST ANALYSIS', className='text-center', style={'color': '#3498DB'}))),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.Div('Crypto', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Period Forward', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Market view 1', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Market view 2', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Target Price', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),

            dbc.Col([
                html.Div(id='CryptoNameSymbol', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
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
                dbc.Input(id='StrikePrice', placeholder='StrikePrice', value=50000, type="number",
                          style={'backgroundColor': 'white', 'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize}),
                dbc.Button('>> Run Chart <<',
                           id='Run_Chart2',
                           color='info',
                           size='sm',
                           className="d-grid gap-2 mx-auto",
                           n_clicks=0),
            ], width={'size': 2, 'offset': 0, 'order': 2}),

            dbc.Col([
                # html.P('Price (USD)', className='text-center'),
                dcc.Graph(id='CryptoForecast',
                          style={'height': 250},
                          config={"displayModeBar": False, "showTips": False}),
                html.Hr(),
                dcc.Graph(id='CryptoPercentage',
                          style={'height': 150},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 8, 'offset': 0, 'order': 3}),

        ], className="mx-3",
        ),

        # -------------------------------------------------------------------------------------------
        # ADDITIONAL INFO
        # -------------------------------------------------------------------------------------------
        html.Hr(),
        dbc.Row(dbc.Col(html.H5('ADDITIONAL INFO', className='text-center', style={'color': '#3498DB'}))),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.Div('Crypto', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Symbol', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Algorithm', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Proof Type', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Launch Date', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                html.Div('Description', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div(id='AddInfoCrypto', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='AddInfoSymbol', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='AddInfoAlg', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='AddInfoProofT', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='AddInfoLDate', className='text-left',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                html.Div(id='AddInfoDescrp', className='text-left',
                         style={'height': '600px', 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
            ], width={'size': 10, 'offset': 0, 'order': 1}),
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


# https://dash.plotly.com/dash-enterprise/static-assets
# https://github.com/plotly/dash/issues/71

# -------------------------------------------------------------------------------------------
# Get Data from CoinGecko - PRICE, VOLUME, MARKET CAP
# -------------------------------------------------------------------------------------------
@app.callback(
            Output(component_id='LastPrice', component_property='children'),
            Output(component_id='DayPerc', component_property='children'),
            Output(component_id='WeekPerc', component_property='children'),
            Output(component_id='YTDPerc', component_property='children'),
            Output(component_id='CryptoPrice', component_property='figure'),
            Output(component_id='CryptoVolume', component_property='figure'),
            Output(component_id='CryptoMarketCap', component_property='figure'),
            Input(component_id='DropdownListCrypto1', component_property='value'),
                    )

def PriceVolumesMarketCap(DropdownListCrypto1):
    cg = CoinGeckoAPI()
    HistoryPrice = cg.get_coin_market_chart_by_id(id=DropdownListCrypto1, vs_currency='usd', interval='daily', days='max')  # max

    # Price
    PriceHist = pd.DataFrame(HistoryPrice['prices'])
    PriceHist.columns = ['Date', 'Price']
    PriceHist['Date'] = pd.to_datetime(PriceHist['Date'], unit='ms')
    PriceHist.drop([len(PriceHist) - 2], inplace=True)

    # Gauge Returns: Daily, Weekly, YTD for first row
    LastPrice = PriceHist.iloc[-1]['Price']

    if LastPrice > 1:
        LastPrice = np.round(LastPrice, 2)
    else:
        LastPrice = np.round(LastPrice, 6)

    LastPrice = '{:,f}'.format(LastPrice)

    DayPerc = '{:,.2%}'.format((PriceHist.iloc[-1]['Price'] / PriceHist.iloc[- 2]['Price']) - 1)
    WeekPerc = '{:,.2%}'.format((PriceHist.iloc[-1]['Price'] / PriceHist.iloc[- 8]['Price']) - 1)
    DaysYTD = min(datetime.now().timetuple().tm_yday, len(PriceHist)) + 1
    YTDPerc = '{:,.2%}'.format((PriceHist.iloc[-1]['Price'] / PriceHist.iloc[- DaysYTD]['Price']) - 1)

    figCryptoPrice = px.area(PriceHist, x='Date', y='Price')
    figCryptoPrice.update_traces(line=dict(color="#3498db", width=1))
    figCryptoPrice.update_xaxes(rangeslider_visible=True)
    figCryptoPrice.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='black'
        )
    )

    figCryptoPrice.update_layout(
                                margin=dict(l=50, t=10), #(l=20, r=20, t=20, b=20)
                                paper_bgcolor="#222222",
    )

    figCryptoPrice.update_layout(
                                xaxis={'showgrid': False},
                                yaxis={'showgrid': False}
    )

    # Volumes
    VolumesHist = pd.DataFrame(HistoryPrice['total_volumes'])
    VolumesHist.columns = ['Date', 'Volumes']
    VolumesHist['Date'] = pd.to_datetime(VolumesHist['Date'], unit='ms')
    VolumesHist.drop([len(VolumesHist) - 2], inplace=True)

    figCryptoVolumes = px.area(VolumesHist, x='Date', y='Volumes')
    figCryptoVolumes.update_traces(line=dict(color="#3498db", width=1))
    figCryptoVolumes.update_xaxes(rangeslider_visible=True)
    figCryptoVolumes.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='black'
        )
    )

    figCryptoVolumes.update_layout(
                                    margin=dict(l=50, t=10), #(l=20, r=20, t=20, b=20)
                                    paper_bgcolor="#222222",
    )

    figCryptoVolumes.update_layout(
                                    xaxis={'showgrid': False},
                                    yaxis={'showgrid': False}
    )

    # MarketCap
    MCapHist = pd.DataFrame(HistoryPrice['market_caps'])
    MCapHist.columns = ['Date', 'Market Cap']
    MCapHist['Date'] = pd.to_datetime(MCapHist['Date'], unit='ms')
    MCapHist.drop([len(MCapHist) - 2], inplace=True)

    figMarketCap = px.area(MCapHist, x='Date', y="Market Cap")
    figMarketCap.update_traces(line=dict(color="#3498db", width=1))
    figMarketCap.update_xaxes(rangeslider_visible=True)
    figMarketCap.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='black'
        )
    )

    figMarketCap.update_layout(
                                margin=dict(l=50, t=10), #(l=20, r=20, t=20, b=20)
                                paper_bgcolor="#222222",
    )

    figMarketCap.update_layout(
                                xaxis={'showgrid': False},
                                yaxis={'showgrid': False}
    )


    return LastPrice, DayPerc, WeekPerc, YTDPerc, \
           figCryptoPrice, figCryptoVolumes, figMarketCap


# -------------------------------------------------------------------------------------------
# CHARTS 1
# -------------------------------------------------------------------------------------------

@app.callback(Output(component_id='CryptoBenchmark', component_property='figure'),
              Output(component_id='CryptoStatistics', component_property='figure'),
              #Output(component_id='CryptoStDev', component_property='figure'),
              #Output(component_id='CryptoSharpeR', component_property='figure'),
              State('CapitalInvest', 'value'),
              [Input(component_id='DropdownListCrypto1', component_property='value'),
               Input(component_id='DropdownListBenchmark1', component_property='value'),
               Input(component_id='DropdownListBenchmark2', component_property='value'),
               Input(component_id='DropdownPeriod', component_property='value'),
               Input(component_id='DropdownRolling', component_property='value'),
               Input(component_id='Statistics1', component_property='value'),
               Input('Run_Chart1', 'n_clicks')
               ]
              )
def Benchmark_Correlation(CapitalInvest,
                          DropdownListCrypto1,
                          DropdownListBenchmark1,
                          DropdownListBenchmark2,
                          DropdownPeriod,
                          DropdownRolling,
                          Statistics1,
                          n
                          ):
    # Invested Capital
    K = CapitalInvest
    Logarithmic = 0  # [0,1]

    # Rolling Days
    Rdays = DropdownRolling

    if DropdownPeriod == '365':
        DDCoingecko = 365
    elif DropdownPeriod == '31':
        DDCoingecko = 31
    elif DropdownPeriod == '91':
        DDCoingecko = 31 * 3
    elif DropdownPeriod == '181':
        DDCoingecko = 181
    elif DropdownPeriod == 'ytd':
        DDCoingecko = datetime.now().timetuple().tm_yday

    # CoinGecko API
    cg = CoinGeckoAPI()

    # Selected Crypto
    HistoryPriceCrypto = cg.get_coin_market_chart_by_id(id=DropdownListCrypto1, vs_currency='usd', interval='daily',
                                                        days=str(DDCoingecko))
    HistoryPriceCrypto = pd.DataFrame(HistoryPriceCrypto['prices'])
    HistoryPriceCrypto.columns = ['Date', DropdownListCrypto1]
    HistoryPriceCrypto['Date'] = pd.to_datetime(HistoryPriceCrypto['Date'], unit='ms')
    HistoryPriceCrypto['Date'] = pd.to_datetime(HistoryPriceCrypto['Date']).dt.date
    HistoryPriceCrypto.drop([len(HistoryPriceCrypto) - 2], inplace=True)

    # Benchmarck 1 (Crypto)
    HistoryPriceBench1 = cg.get_coin_market_chart_by_id(id=DropdownListBenchmark1, vs_currency='usd', interval='daily',
                                                        days=str(DDCoingecko))
    HistoryPriceBench1 = pd.DataFrame(HistoryPriceBench1['prices'])
    HistoryPriceBench1.columns = ['Date', DropdownListBenchmark1]
    HistoryPriceBench1['Date'] = pd.to_datetime(HistoryPriceBench1['Date'], unit='ms')
    HistoryPriceBench1['Date'] = pd.to_datetime(HistoryPriceBench1['Date']).dt.date
    HistoryPriceBench1.drop([len(HistoryPriceBench1) - 2], inplace=True)

    # Join Crypto1 e Benchmark 1
    HistoryPriceCrypto = HistoryPriceCrypto.join(HistoryPriceBench1.set_index('Date'), on='Date')

    # Benchmarck 2 (Crypto)
    HistoryPriceBench2 = cg.get_coin_market_chart_by_id(id=DropdownListBenchmark2, vs_currency='usd', interval='daily',
                                                        days=str(DDCoingecko))
    HistoryPriceBench2 = pd.DataFrame(HistoryPriceBench2['prices'])
    HistoryPriceBench2.columns = ['Date', DropdownListBenchmark2]
    HistoryPriceBench2['Date'] = pd.to_datetime(HistoryPriceBench2['Date'], unit='ms')
    HistoryPriceBench2['Date'] = pd.to_datetime(HistoryPriceBench2['Date']).dt.date
    HistoryPriceBench2.drop([len(HistoryPriceBench2) - 2], inplace=True)

    # Join Crypto e Benchmark 2
    HistoryPriceCrypto = HistoryPriceCrypto.join(HistoryPriceBench2.set_index('Date'), on='Date')
    # HistoryPriceCrypto.round({DropdownListCrypto1: 2, DropdownListBenchmark1: 2, DropdownListBenchmark2: 2})

    # Clean NaN for Benchmark 2
    # HistoryPriceCrypto[DropdownListBenchmark2] = HistoryPriceCrypto[DropdownListBenchmark2].fillna(method='pad')
    # HistoryPriceCrypto[DropdownListBenchmark2] = HistoryPriceCrypto[DropdownListBenchmark2].fillna(method='bfill')

    # Manage DataFrame
    Ann = 365

    # Index K
    HistoryPriceCrypto['Index_' + DropdownListCrypto1] = HistoryPriceCrypto[DropdownListCrypto1] / \
                                                         HistoryPriceCrypto.iloc[0][DropdownListCrypto1] * K
    HistoryPriceCrypto['Index_' + DropdownListBenchmark1] = HistoryPriceCrypto[DropdownListBenchmark1] / \
                                                            HistoryPriceCrypto.iloc[0][DropdownListBenchmark1] * K
    HistoryPriceCrypto['Index_' + DropdownListBenchmark2] = HistoryPriceCrypto[DropdownListBenchmark2] / \
                                                            HistoryPriceCrypto.iloc[0][DropdownListBenchmark2] * K

    # Returns, Correlation, ...
    HistoryPriceCrypto[['R_' + DropdownListCrypto1, 'R_' + DropdownListBenchmark1, 'R_' + DropdownListBenchmark2]] = \
        HistoryPriceCrypto[[DropdownListCrypto1, DropdownListBenchmark1, DropdownListBenchmark2]].pct_change()

    # Rolling St. Dev
    HistoryPriceCrypto['Std_' + DropdownListCrypto1] = HistoryPriceCrypto['R_' + DropdownListCrypto1].rolling(
        Rdays).std() * np.sqrt(Ann)
    HistoryPriceCrypto['Std_' + DropdownListBenchmark1] = HistoryPriceCrypto['R_' + DropdownListBenchmark1].rolling(
        Rdays).std() * np.sqrt(Ann)
    HistoryPriceCrypto['Std_' + DropdownListBenchmark2] = HistoryPriceCrypto['R_' + DropdownListBenchmark2].rolling(
        Rdays).std() * np.sqrt(Ann)

    # Rolling Sharpe
    HistoryPriceCrypto['Sharpe' + DropdownListCrypto1] = HistoryPriceCrypto['R_' + DropdownListCrypto1].rolling(
        Rdays).mean() / \
                                                         HistoryPriceCrypto['R_' + DropdownListCrypto1].rolling(
                                                             Rdays).std()
    HistoryPriceCrypto['Sharpe' + DropdownListBenchmark1] = HistoryPriceCrypto['R_' + DropdownListBenchmark1].rolling(
        Rdays).mean() / \
                                                            HistoryPriceCrypto['R_' + DropdownListBenchmark1].rolling(
                                                                Rdays).std()
    HistoryPriceCrypto['Sharpe' + DropdownListBenchmark2] = HistoryPriceCrypto['R_' + DropdownListBenchmark2].rolling(
        Rdays).mean() / \
                                                            HistoryPriceCrypto['R_' + DropdownListBenchmark2].rolling(
                                                                Rdays).std()

    # Rolling Correlation
    HistoryPriceCrypto['Corr. ' + DropdownListCrypto1 + ' - ' + DropdownListBenchmark1] = HistoryPriceCrypto[
        'R_' + DropdownListCrypto1].rolling(Rdays).corr(HistoryPriceCrypto['R_' + DropdownListBenchmark1])
    HistoryPriceCrypto['Corr. ' + DropdownListCrypto1 + ' - ' + DropdownListBenchmark2] = HistoryPriceCrypto[
        'R_' + DropdownListCrypto1].rolling(Rdays).corr(HistoryPriceCrypto['R_' + DropdownListBenchmark2])

    # Plotly Index Base K
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Index_' + DropdownListCrypto1],
                   name=DropdownListCrypto1, line=dict(color='#3498db', width=1)))
    fig1.add_trace(
        go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Index_' + DropdownListBenchmark1],
                   name=DropdownListBenchmark1, line=dict(color='blue', width=1)))
    fig1.add_trace(
        go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Index_' + DropdownListBenchmark2],
                   name=DropdownListBenchmark2, line=dict(color='#248f8f', width=1)))

    fig1.update_layout(title='Capital Invested: ' + str(K) + ' USD', font=dict(size=10),
                       legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))

    if Logarithmic == 1:
        fig1.update_layout(yaxis_type="log")


    fig1.update_layout(
        margin=dict(l=50, t=10), #(l=20, r=20, t=20, b=20)
        paper_bgcolor="#222222",
    )

    fig1.update_layout(
        xaxis={'showgrid': False},
        yaxis={'showgrid': False}
    )


    if Statistics1 == 1:
        # Std Deviation
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Std_' + DropdownListCrypto1],
                       name=(DropdownListCrypto1), line=dict(color='#3498db', width=1)))
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Std_' + DropdownListBenchmark1],
                       name=(DropdownListBenchmark1), line=dict(color='blue', width=1)))
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Std_' + DropdownListBenchmark2],
                       name=(DropdownListBenchmark2), line=dict(color='#248f8f', width=1)))

        fig2.update_layout(title='Rolling Volatility ' + str(Rdays) + ' days', font=dict(size=10),
                           legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))
        fig2.update_layout(yaxis_tickformat='.2%')

    elif Statistics1 == 2:
        # Correltation Crypto vs. Benchmarks (1,2)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'],
                       y=HistoryPriceCrypto['Corr. ' + DropdownListCrypto1 + ' - ' + DropdownListBenchmark1],
                       name=(DropdownListCrypto1 + ' & ' + DropdownListBenchmark1), line=dict(color='#3498db', width=1)))
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'],
                       y=HistoryPriceCrypto['Corr. ' + DropdownListCrypto1 + ' - ' + DropdownListBenchmark2],
                       name=(DropdownListCrypto1 + ' & ' + DropdownListBenchmark2), line=dict(color='blue', width=1)))

        fig2.update_layout(title='Rolling Correlation ' + str(Rdays) + ' days', font=dict(size=10),
                           legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))
        fig2.update_layout(yaxis_tickformat='.2%')

    elif Statistics1 == 3:
        # Sharpe Ratio
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Sharpe' + DropdownListCrypto1],
                       name=(DropdownListCrypto1), line=dict(color='#3498db', width=1)))
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Sharpe' + DropdownListBenchmark1],
                       name=(DropdownListBenchmark1), line=dict(color='blue', width=1)))
        fig2.add_trace(
            go.Scatter(x=HistoryPriceCrypto['Date'], y=HistoryPriceCrypto['Sharpe' + DropdownListBenchmark2],
                       name=(DropdownListBenchmark2), line=dict(color='#248f8f', width=1)))

        fig2.update_layout(title='Rolling Sharpe Ratio ' + str(Rdays) + ' days', font=dict(size=10),
                           legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))

    fig2.update_layout(
        margin=dict(l=50, t=10), #(l=20, r=20, t=20, b=20)
        paper_bgcolor="#222222",
    )

    fig2.update_layout(
        xaxis={'showgrid': False},
        yaxis={'showgrid': False}
    )

    return fig1, fig2

# -------------------------------------------------------------------------------------------
# CHARTS 2: FORECAST
# -------------------------------------------------------------------------------------------
@app.callback(Output(component_id='CryptoNameSymbol', component_property='children'),
              Output(component_id='CryptoForecast', component_property='figure'),
              Output(component_id='CryptoPercentage', component_property='figure'),
              [Input(component_id='DropdownListCrypto1', component_property='value'),
               Input(component_id='PeriodForward', component_property='value'),
               Input(component_id='MarketView1', component_property='value'),
               Input(component_id='MarketView2', component_property='value'),
               Input('Run_Chart2', 'n_clicks')
               ],
               State('StrikePrice', 'value'),
              )

def ForecastAnalysis(DropdownListCrypto1,
                      PeriodForward,
                      MarketView1,
                      MarketView2,
                      n,
                      StrikePrice
                      ):

    File_In_Name = '2021.12.24_CoinGeko_List_Symbol.xlsx'
    Sheet_Name_In = 'DataSet'
    CryptoSymbolDf = pd.read_excel(File_In_Name, sheet_name=Sheet_Name_In, engine='openpyxl')

    CryptoName = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['name'].values[0]
    CryptoSym = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['symbolCapital'].values[0]
    CryptoNameSymbol = CryptoName + ' (' + CryptoSym + ')'

    Period = 365
    Np = 500
    T = PeriodForward
    Dt = 1
    Nmu = 0
    Nsigma = 1
    Strike = StrikePrice

    SelectTrend1 = MarketView1  # bull, flat, bear
    SelectTrend2 = MarketView2  # bull, flat, bear

    # run code
    cg = CoinGeckoAPI()
    HistoryPriceC = cg.get_coin_market_chart_by_id(id=DropdownListCrypto1, vs_currency='usd', interval='daily',
                                                   days=str(Period))

    # price vector
    PriceHistC = pd.DataFrame(HistoryPriceC['prices'])
    PriceHistC.columns = ['Date', 'Price']
    PriceHistC['Date'] = pd.to_datetime(PriceHistC['Date'], unit='ms')
    PriceHistC['Date'] = pd.to_datetime(PriceHistC['Date']).dt.date
    PriceHistC.drop([Period - 1], inplace=True)
    PriceHistC['Ones'] = 1
    PriceHistC['Strike'] = Strike

    #LastPrice = PriceHistC.iloc[Period - 1]['Price']
    #LastDate = PriceHistC.iloc[Period - 1]['Date']

    LastPrice = PriceHistC.iloc[- 1]['Price']
    LastDate = PriceHistC.iloc[- 1]['Date']

    # Return n Stdev
    PriceHistC['Ret'] = PriceHistC['Price'].pct_change()
    Mu = PriceHistC['Ret'].mean()
    DevStd = PriceHistC['Ret'].std()

    # Def Trend 1
    if SelectTrend1 == 1:
        Mu1 = PriceHistC['Ret'].mean()
    elif SelectTrend1 == 2:
        Mu1 = 0
    elif SelectTrend1 == 3:
        Mu1 = (PriceHistC['Ret'].mean() / 2) * -1

    # Def Trend 2
    if SelectTrend2 == 1:
        Mu2 = PriceHistC['Ret'].mean()
    elif SelectTrend2 == 2:
        Mu2 = 0
    elif SelectTrend2 == 3:
        Mu2 = (PriceHistC['Ret'].mean() / 2) * -1

    # GBM
    GBMmatrix = np.zeros((Np, T))
    GBMmatrix[:, 0] = LastPrice

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
    GBMmatrixPerc = GBMmatrix.copy()
    GBMmatrixPerc = GBMmatrixPerc - Strike
    GBMmatrixPerc[GBMmatrixPerc >= 0] = 1
    GBMmatrixPerc[GBMmatrixPerc < 0] = 0
    V_sum = pd.DataFrame(GBMmatrixPerc.sum()) / len(GBMmatrixPerc)
    V_sum = V_sum.reset_index()
    V_sum['index1'] = pd.date_range(start=LastDate, periods=T, freq='D')

    # Matrix for Area chart
    Plot_Matrix = pd.DataFrame()
    Plot_Matrix['index1'] = pd.date_range(start=LastDate, periods=T, freq='D')
    Plot_Matrix['Min'] = GBMmatrix.quantile(.05) #pd.DataFrame(GBMmatrix.min())
    Plot_Matrix['Max'] = GBMmatrix.quantile(.95) #pd.DataFrame(GBMmatrix.max())
    Plot_Matrix['Average Price'] = pd.DataFrame(GBMmatrix.mean())
    Plot_Matrix['Price Q1'] = GBMmatrix.quantile(.1)
    #Plot_Matrix['Price Q2'] = GBMmatrix.quantile(.2)
    Plot_Matrix['Price Q3'] = GBMmatrix.quantile(.3)
    Plot_Matrix['Price Q4'] = GBMmatrix.quantile(.7)
    #Plot_Matrix['Price Q5'] = GBMmatrix.quantile(.8)
    Plot_Matrix['Price Q6'] = GBMmatrix.quantile(.9)
    Plot_Matrix['Strike'] = Strike

    # Chart Area
    # https://plotly.com/python/filled-area-plots/
    fig5 = go.Figure()
    fig5.add_trace(
        go.Scatter(x=PriceHistC['Date'], y=PriceHistC['Price'], name='Historical Price', fill='none', mode='lines',
                   line=dict(width=1, color='#3498db')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Min'], name='', fill='none', mode='lines',
                   line=dict(width=0, color='black')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q1'], name='Worst 10% chance', fill='tonexty',
                   mode='lines', line=dict(width=0, color='red')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q3'], name='20% chance', fill='tonexty', mode='lines',
                   line=dict(width=0, color='orange')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q4'], name='40% chance - Most Likely', fill='tonexty', mode='lines',
                   line=dict(width=0, color='yellow')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Price Q6'], name='20% chance', fill='tonexty', mode='lines',
                   line=dict(width=0, color='yellowgreen')))
    fig5.add_trace(
        go.Scatter(x=Plot_Matrix['index1'], y=Plot_Matrix['Max'], name='Best 10% chance', fill='tonexty', mode='lines',
                   line=dict(width=0, color='lightgreen')))

    fig5.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1, font=(dict(size=9.5))))
    fig5.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222")
    fig5.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    # probability
    fig6 = go.Figure()
    fig6.add_trace(
        go.Scatter(x=V_sum['index1'], y=V_sum[0], name='Probability over ' + '{:,.2f}'.format(Strike) + ' USD', fill='tonexty',
                   mode='lines', line=dict(width=1, color='#3498db')))
    fig6.add_trace(go.Scatter(x=PriceHistC['Date'], name='', y=PriceHistC['Ones'], fill='none', mode='none'))

    fig6.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))
    fig6.update_layout(yaxis_tickformat='.2%')
    fig6.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222") # https://plotly.com/python/setting-graph-size/#adjusting-height-width--margins
    fig6.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    return CryptoNameSymbol, fig5, fig6


# -------------------------------------------------------------------------------------------
# ADDITIONAL INFO
# -------------------------------------------------------------------------------------------

@app.callback(
            Output(component_id='AddInfoCrypto', component_property='children'),
            Output(component_id='AddInfoSymbol', component_property='children'),
            Output(component_id='AddInfoAlg', component_property='children'),
            Output(component_id='AddInfoProofT', component_property='children'),
            Output(component_id='AddInfoLDate', component_property='children'),
            Output(component_id='AddInfoDescrp', component_property='children'),
            #Output(component_id='xxx', component_property='children'),
            Input(component_id='DropdownListCrypto1', component_property='value'),
                    )

def AdditionalInfo(DropdownListCrypto1):

    File_In_Name = '2021.12.24_CoinGeko_List_Symbol_Plus_CoinMarketCap.xlsx'
    Sheet_Name_In = 'DataSet'
    CryptoSymbolDf = pd.read_excel(File_In_Name, sheet_name=Sheet_Name_In, engine='openpyxl')

    AddInfoCrypto = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['name'].values[0]
    AddInfoSymbol = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['symbolCapital'].values[0]
    AddInfoAlg = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['Algorithm'].values[0]
    AddInfoProofT = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['ProofType'].values[0]
    AddInfoLDate = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['AssetLaunchDate'].values[0]
    AddInfoDescrp = CryptoSymbolDf.loc[(CryptoSymbolDf['id'] == DropdownListCrypto1)]['Description'].values[0]

    return AddInfoCrypto, AddInfoSymbol, AddInfoAlg, AddInfoProofT, AddInfoLDate, AddInfoDescrp

# -------------------------------------------------------------------------------------------
#                                         --- END ---
# -------------------------------------------------------------------------------------------