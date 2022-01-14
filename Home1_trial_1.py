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



#https://plotly.com/python/time-series/

#editable table: https://dash.plotly.com/datatable/editable

# -------------------------------------------------------------------------------------------
#                                       *** LIBRARIES ***
# -------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import time
from datetime import date, datetime, timezone
import base64

# Google Trends
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)

# CoinGecko
from pycoingecko import CoinGeckoAPI

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
#import dash_core_components as dcc

# Multipage
from app import app

# -------------------------------------------------------------------------------------------
#                                       *** DATA ***
# -------------------------------------------------------------------------------------------

# Get Logo
image_filename = 'QUANTUMBLOCKAI_1.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


# -------------------------------------------------------------------------------------------
# Get Data from CoinGeko
# -------------------------------------------------------------------------------------------

TableColumns = ['Rank', 'Currency', 'Symbol', 'Price (USD)', 'Change 24H (%)', 'ATH (USD)', 'ATH Change (%)',
                'Market Cap (USDm)', 'Supply in %']

# -------------------------------------------------------------------------------------------
#                                       *** DASH APP ***
# -------------------------------------------------------------------------------------------
# Style
load_figure_template('darkly')
HeightIndicators = 80
FontSize = 13
HeightDiv = '35px'
MarginBDiv = 7
PaddingTopDiv = 8
HeightDrop = '25px'
MarginBDrop = 17

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

layout = dbc.Container(
    [

        html.Hr(),
        # Header
        dbc.Row(dbc.Col(html.H5('OVERVIEW', className='text-center', style={'color': '#3498DB'}))), # text-primary, mb-3'))), # header row
        html.Hr(),

        # First row
        #html.P('Google Trends for Gold, Bitcoin and Ethereum', className='text-center'),
        dbc.Row([
            dbc.Col([
                html.Div('Google Trends Analysis', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                dcc.Graph(id='goolgetrendslinechart',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.Div('Bitcoin Market Cap (USD)', className='text-center', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
                dcc.Graph(id='BitcoinMarketCap',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.Div('Ethereum Market Cap (USD)', className='text-center',
                         style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize,
                                'paddingTop': PaddingTopDiv}),
                dcc.Graph(id='EthereumMarketCap',
                          style={'height': 200},
                          config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 4, 'offset': 0, 'order': 3}),
        ], className="mx-3",
        ),

        html.Hr(),
        dbc.Row(dbc.Col(html.H5('TOP CRYPTO TO FOLLOW', className='text-center', style={'color': '#3498DB'}))),  # text-primary, mb-3'))), # header row
        html.P(),
        # Second row
        dbc.Row([
            dbc.Col([
                #html.P(),
                html.Div('Top 5 Crypto by Market Cap', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='indicators0', style={'height': HeightIndicators}, config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 10, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),
        # Third row
        dbc.Row([
            dbc.Col([
                #html.P(),
                html.Div('🔥 Top 5 Crypto on 🔥', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='indicators1', style={'height': HeightIndicators}, config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 10, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),
        # Forth row
        dbc.Row([
            dbc.Col([
                #html.P(),
                html.Div('↘️ Bottom 5 Crypto ↘️', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='indicators2', style={'height': HeightIndicators}, config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 10, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),
        # Fifth row
        dbc.Row([
            dbc.Col([
                #html.P(),
                html.Div('⭐ Top 5 Crypto watchlist ⭐', className='text-left', style={'height': HeightDiv, 'marginBottom': MarginBDiv, 'fontSize': FontSize, 'paddingTop': PaddingTopDiv}),
            ], width={'size': 2, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='indicators3', style={'height': HeightIndicators}, config={"displayModeBar": False, "showTips": False}),
            ], width={'size': 10, 'offset': 0, 'order': 2}),
        ], className="mx-3",
        ),

        # Table
        html.Hr(),
        dbc.Row(dbc.Col(html.H5('TOP 250 CRYPTO', className='text-center', style={'color': '#3498DB'}))),  # text-primary, mb-3'))), # header row

        dbc.Row(
            [
                dbc.Col(dt.DataTable(
                    id='table',
                    data=[],
                    columns=[{"name": i, "id": i} for i in TableColumns],
                    style_as_list_view=True,
                    filter_action='native',
                    page_action='native',
                    page_current=0,
                    page_size=250,
                    #sort_action='custom',
                    #sort_mode='single',
                    #sort_by=[],
                    style_header={'backgroundColor': 'rgb(52, 152, 219)', 'color': 'white', 'fontWeight': 'bold',
                                  'textAlign': 'left', 'border': '1px solid black'},
                    fixed_rows={'headers': True},
                    style_data={'color': 'white', 'backgroundColor': 'rgb(34, 34, 34)','textAlign': 'left', 'border': '1px solid black'},
                    style_cell={'fontSize': FontSize, 'minWidth': '40px', 'width': '100px', 'maxWidth': '400px', 'whiteSpace': 'normal'},  # '25%'
                    # fill_width=False,
                    style_table={'minHeight': 1000, 'overflowX': 'auto', 'overflowY': 'off'},
                    # style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
                    # style={'width': '80%', 'marginLeft': '25%', 'marginTop': 20, 'marginBottom': 20},
                    style_data_conditional=[
                        # Change 24H (%) > 0
                        {
                            'if': {
                                'filter_query': '{Change 24H (%)} > ' + str(0),
                                'column_id': 'Change 24H (%)'},
                            'color': 'green',
                        },

                        # Change 24H (%) < 0
                        {
                            'if': {
                                'filter_query': '{Change 24H (%)} < ' + str(0),
                                'column_id': 'Change 24H (%)'},
                            'color': 'red',
                        },

                    ],
                ), width=12,
                ),
            ], #className="mx-1",
        ),

        html.Hr(),
        # Closing
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


        #https://dash.plotly.com/live-updates
        # Interval for CoinGecko
        dcc.Interval(
            id='interval-component',
            interval=5 * (60 * 1000), # in milliseconds #1000: 1 sec #60: 1 min
            n_intervals=0),

        # Interval for Google Trends
        dcc.Interval(
            id='interval-component_1',
            interval=24 * 60 * (60 * 1000),  # in milliseconds #1000: 1 sec #60: 1 min
            n_intervals=0),

    ], fluid=True)



#https://dash.plotly.com/dash-enterprise/static-assets
#https://github.com/plotly/dash/issues/71

#@app.callback(Output(component_id='scenari_plot', component_property='figure'))


# -------------------------------------------------------------------------------------------
# Get Data from GoogleTrends
# -------------------------------------------------------------------------------------------

@app.callback(
              Output(component_id='goolgetrendslinechart', component_property='figure'),
              Input(component_id='interval-component_1', component_property='n_intervals')
             )

def GoogleTrends(aa):

    kw_list = ['Gold', 'Bitcoin', 'Ethereum']
    Cat = 0
    TimeFrame = 'all' #'today 10-y' #dropdowngoogletrendstime #'today 5-y' #'today 3-m'  # 'today 1-m' #'all' #'today 5-y'
    Geo = ''  # , 'FR', 'ES', 'HK', 'KR']
    GProp = ''

    pytrends.build_payload(kw_list, cat=Cat, timeframe=TimeFrame, geo=Geo, gprop=GProp)
    Df = pytrends.interest_over_time()
    Df.drop(labels=['isPartial'], axis=1, inplace=True)

    # https://community.plotly.com/t/plotly-express-line-chart-color/27333/3
    figGoogleTrend = px.line(Df,
                             color_discrete_map={
                                 "Gold": "#3498DB",
                                 "Bitcoin": "#f2a900",
                                 "Ethereum": "#ecf0f1",
                                                },
                             )
    figGoogleTrend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
    figGoogleTrend.update_xaxes(rangeslider_visible=True)
    figGoogleTrend.update_traces(line=dict(width=1))
    figGoogleTrend.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222")
    figGoogleTrend.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})


    return figGoogleTrend

# -------------------------------------------------------------------------------------------
# Get Data from CoinGecko - MARKET CAP
# -------------------------------------------------------------------------------------------
@app.callback(
              Output(component_id='BitcoinMarketCap', component_property='figure'),
              Output(component_id='EthereumMarketCap', component_property='figure'),
              Input(component_id='interval-component_1', component_property='n_intervals')
             )

def BitcoinMarketCap(aa):

    cg = CoinGeckoAPI()
    # Bitcoin
    HistoryPrice = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days='max')  # max

    MCapHist = pd.DataFrame(HistoryPrice['market_caps'])
    MCapHist.columns = ['Date', 'Market Cap']
    MCapHist['Date'] = pd.to_datetime(MCapHist['Date'], unit='ms')

    figBitcoinMarketCap = px.area(MCapHist, x='Date', y="Market Cap")
    figBitcoinMarketCap.update_traces(line=dict(color="#3498db", width=1))
    figBitcoinMarketCap.update_xaxes(rangeslider_visible=True)
    figBitcoinMarketCap.update_xaxes(
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

    figBitcoinMarketCap.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222")
    figBitcoinMarketCap.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    # Ethereum
    HistoryPrice = cg.get_coin_market_chart_by_id(id='ethereum', vs_currency='usd', days='max')  # max

    MCapHist = pd.DataFrame(HistoryPrice['market_caps'])
    MCapHist.columns = ['Date', 'Market Cap']
    MCapHist['Date'] = pd.to_datetime(MCapHist['Date'], unit='ms')

    figEthereumMarketCap = px.area(MCapHist, x='Date', y="Market Cap")
    figEthereumMarketCap.update_traces(line=dict(color="#3498db", width=1))
    figEthereumMarketCap.update_xaxes(rangeslider_visible=True)
    figEthereumMarketCap.update_xaxes(
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

    figEthereumMarketCap.update_layout(margin=dict(l=50, t=10), paper_bgcolor="#222222")
    figEthereumMarketCap.update_layout(xaxis={'showgrid': False}, yaxis={'showgrid': False})

    return figBitcoinMarketCap, figEthereumMarketCap


# -------------------------------------------------------------------------------------------
# Get Data from CoinGecko - INDICATORS
# -------------------------------------------------------------------------------------------
@app.callback(
              Output(component_id='indicators0', component_property='figure'),
              Output(component_id='indicators1', component_property='figure'),
              Output(component_id='indicators2', component_property='figure'),
              Output(component_id='indicators3', component_property='figure'),
              Output("table", "data"),
              #Output(component_id='table', component_property='data'),
              Input(component_id='interval-component', component_property='n_intervals')
             )

def CoinGeko(n_intervals):
    cg = CoinGeckoAPI()
    MarketData = cg.get_coins_markets(vs_currency='usd', per_page=250, page=1)
    MarketData = pd.DataFrame(MarketData)
    #print(MarketData)

    MarketData['Supply in %'] = MarketData['circulating_supply'] / MarketData['total_supply']
    #MarketData[['Circulating Supply %']] = MarketData[['Circulating Supply %']]. fillna('')
    MarketData['symbol'] = MarketData['symbol'].str.upper()
    MarketData['market_cap'] = MarketData['market_cap'] / 10 ** 9
    #print(MarketData.columns)

    #MarketData.set_index('market_cap_rank', inplace=True)
    MarketData.drop(['id', 'image', 'fully_diluted_valuation', 'total_volume', 'high_24h', 'low_24h', 'price_change_24h', 'market_cap_change_24h', 'market_cap_change_percentage_24h', 'max_supply', 'atl', 'atl_change_percentage', 'atl_date', 'roi', 'last_updated','ath_date','circulating_supply', 'total_supply'], axis=1, inplace=True)
    MarketData = MarketData[['market_cap_rank', 'name', 'symbol', 'current_price', 'price_change_percentage_24h', 'ath', 'ath_change_percentage', 'market_cap', 'Supply in %']]
    MarketData.rename(columns={'market_cap_rank': 'Rank',
                               'name': 'Currency',
                               'symbol': 'Symbol',
                               'current_price': 'Price (USD)',
                               'price_change_percentage_24h': 'Change 24H (%)',
                               'ath': 'ATH (USD)',
                               'ath_change_percentage': 'ATH Change (%)',
                               'market_cap': 'Market Cap (USDm)'
                                }, inplace=True)

    MarketData = MarketData.round({'Change 24H (%)': 2, 'Supply in %': 4, 'ATH Change (%)': 2, 'Market Cap (USDm)': 2})

    # Sort Change 24H % Max
    Max_MarketData = MarketData.copy()
    Max_MarketData.sort_values(by=['Change 24H (%)'], ascending=False, inplace=True)

    # Sort Change 24H % min
    Min_MarketData = MarketData.copy()
    Min_MarketData.sort_values(by=['Change 24H (%)'], ascending=True, inplace=True)

    CHART_THEME = 'plotly_dark'

    # indicators margins
    Indleft = 100
    Indright = 100
    Indbtop = 0
    Indbottom = 0
    SizeNumberIndicator = 20
    SizeTextIndicator = 2.5

    n = 5

    # 1 - Top 5 Crypto by MarketCap
    # Get data
    Names = [''] * n
    Prices = [0] * n
    Delta = [0] * n
    for i in range(n):
        Names[i] = MarketData.iloc[i]['Currency']
        Prices[i] = MarketData.iloc[i]['Price (USD)']
        Delta[i] = Prices[i] / (1 + (MarketData.iloc[i]['Change 24H (%)']) / 100)

    # Create indicators
    Ind_Horizontal_v0 = go.Figure()
    Ind_Horizontal_v0.layout.template = CHART_THEME
    for i in range(n):
        Ind_Horizontal_v0.add_trace(go.Indicator(
            mode="number+delta",
            value=Prices[i],
            number={'valueformat': ',.f', "font": {"size": SizeNumberIndicator}},
            delta={'position': "bottom", 'reference': Delta[i], 'relative': True},  #'valueformat': '.2f'},
            title={"text": "<br><span style='font-size:" + str(SizeTextIndicator) + "em;color:gray'>" + Names[i] + "</span>"},
            domain={'row': 0, 'column': i}))

    Ind_Horizontal_v0.update_layout(
        grid = {'rows': 1, 'columns': 5, 'pattern': "independent"},
        margin=dict(l=Indleft, r=Indright, t=Indbtop, b=Indbottom))
    Ind_Horizontal_v0.update_layout(paper_bgcolor="#222222")

    # 2 - Top 5 Crypto Gains
    # Get data
    Names1 = [''] * n
    Prices1 = [0] * n
    Delta1 = [0] * n
    for i in range(n):
        Names1[i] = Max_MarketData.iloc[i]['Currency']
        Prices1[i] = Max_MarketData.iloc[i]['Price (USD)']
        Delta1[i] = Prices1[i] / (1 + (Max_MarketData.iloc[i]['Change 24H (%)']) / 100)

    # Create indicators
    Ind_Horizontal_v1 = go.Figure()
    Ind_Horizontal_v1.layout.template = CHART_THEME
    for i in range(n):
        Ind_Horizontal_v1.add_trace(go.Indicator(
            mode="number+delta",
            value=Prices1[i],
            number={'valueformat': ',.f', "font": {"size": SizeNumberIndicator}},
            delta={'position': "bottom", 'reference': Delta1[i], 'relative': True},  #'valueformat': '.2f'},
            title={"text": "<br><span style='font-size:" + str(SizeTextIndicator) + "em;color:gray'>" + Names1[i] + "</span>"},
            domain={'row': 0, 'column': i}))

    Ind_Horizontal_v1.update_layout(
        grid = {'rows': 1, 'columns': 5, 'pattern': "independent"},
        margin=dict(l=Indleft, r=Indright, t=Indbtop, b=Indbottom))
    Ind_Horizontal_v1.update_layout(paper_bgcolor="#222222")

    # 3 - Worst 5 Crypto Gains
    # Get data
    Names2 = [''] * n
    Prices2 = [0] * n
    Delta2 = [0] * n
    for i in range(n):
        Names2[i] = Min_MarketData.iloc[i]['Currency']
        Prices2[i] = Min_MarketData.iloc[i]['Price (USD)']
        Delta2[i] = Prices2[i] / (1 + (Min_MarketData.iloc[i]['Change 24H (%)']) / 100)

    # Create indicators
    Ind_Horizontal_v2 = go.Figure()
    Ind_Horizontal_v2.layout.template = CHART_THEME
    for i in range(n):
        Ind_Horizontal_v2.add_trace(go.Indicator(
            mode="number+delta",
            value=Prices2[i],
            number={'valueformat': ',.f', "font": {"size": SizeNumberIndicator}},
            delta={'position': "bottom", 'reference': Delta2[i], 'relative': True},  #'valueformat': '.2f'},
            title={"text": "<br><span style='font-size:" + str(SizeTextIndicator) + "em;color:gray'>" + Names2[i] + "</span>"},
            domain={'row': 0, 'column': i}))

    Ind_Horizontal_v2.update_layout(
        grid = {'rows': 1, 'columns': 5, 'pattern': "independent"},
        margin=dict(l=Indleft, r=Indright, t=Indbtop, b=Indbottom))
    Ind_Horizontal_v2.update_layout(paper_bgcolor="#222222")

    # 4 - Watchlist Crypto
    # Get data
    Names3 = ['Cardano', 'Polkadot', 'Terra', 'Uniswap', 'Avalanche']
    Prices3 = [0] * n
    Delta3 = [0] * n

    for i in range(n):
        P = MarketData.loc[MarketData['Currency'] == Names3[i]]['Price (USD)']
        Prices3[i] = P.iloc[0]
        D = MarketData.loc[MarketData['Currency'] == Names3[i]]['Change 24H (%)']
        D = D.iloc[0] / 100
        Delta3[i] = Prices3[i] / (1 + D)

    # Create indicators
    Ind_Horizontal_v3 = go.Figure()
    Ind_Horizontal_v3.layout.template = CHART_THEME
    for i in range(n):
        Ind_Horizontal_v3.add_trace(go.Indicator(
            mode="number+delta",
            value=Prices3[i],
            number={'valueformat': ',.f', "font": {"size": SizeNumberIndicator}},
            delta={'position': "bottom", 'reference': Delta3[i], 'relative': True},  #'valueformat': '.2f'},
            title={"text": "<br><span style='font-size:" + str(SizeTextIndicator) + "em;color:gray'>" + Names3[i] + "</span>"},
            domain={'row': 0, 'column': i}))

    Ind_Horizontal_v3.update_layout(
        grid = {'rows': 1, 'columns': 5, 'pattern': "independent"},
        margin=dict(l=Indleft, r=Indright, t=Indbtop, b=Indbottom))
    Ind_Horizontal_v3.update_layout(paper_bgcolor="#222222")

    # For Table layout format
    #https://stackoverflow.com/questions/54110289/pandas-dataframe-column-of-floats-to-percentage-style-error
    MarketData['Supply in %'] = MarketData['Supply in %'].astype(float).map("{:.2%}".format)
    MarketData['Change 24H (%)'] = pd.to_numeric(MarketData['Change 24H (%)'],errors='coerce') / 100
    MarketData['Change 24H (%)'] = MarketData['Change 24H (%)'].astype(float).map("{:.2%}".format)
    MarketData['ATH Change (%)'] = pd.to_numeric(MarketData['ATH Change (%)'],errors='coerce') / 100
    MarketData['ATH Change (%)'] = MarketData['ATH Change (%)'].astype(float).map("{:.2%}".format)

    Data = MarketData.to_dict('records')

    return Ind_Horizontal_v0, Ind_Horizontal_v1, Ind_Horizontal_v2, Ind_Horizontal_v3, Data


#if __name__ == "__main__":
#    app.run_server(debug=True)

# -------------------------------------------------------------------------------------------
#                                         --- END ---
# -------------------------------------------------------------------------------------------