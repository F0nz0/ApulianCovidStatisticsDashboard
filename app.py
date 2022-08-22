'''
2021 Jan 30. Author: Fonz0

######################################
# Apulian Covid Real-time DashBoard. #
######################################
A web application based on Dash and Flask frameworks to visualize
daily-updated Covid epidemiologic data of Apulia Italian Region,
retrieved from the public GithHub Repository of the "Protezione Civile Italiana".
'''

# import dependency
import pandas as pd
import plotly.express as px
import webbrowser
from functions.utils import retrieve_data
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from urllib.request import urlopen
import json


# download dati da repository Protezione Civile Italiana (GitHub)
print('Downloading datasets from the GitHub repository of the "Protezione Civile Italiana"\nand elaborating them........')
try:
    df_italia, df_regioni, df_province, df_province_coord, df_prov_map = retrieve_data()
    print('Data have been succefully retrieved and elaborated!')
except:
    print("ERRROR!\nIt hasn't been possible to retrive and/or elaborate the data.")

# dati Puglia
df_puglia = df_regioni[df_regioni["denominazione_regione"]=="Puglia"].sort_values(by="data")
df_puglia.data = pd.to_datetime(df_puglia.data)
df_puglia.set_index("data", inplace=True)

# dati Italia
df_italia["data"] = pd.to_datetime(df_italia["data"])
df_italia.sort_values(by="data")
df_italia.set_index("data", inplace=True)

# Figura Mappa Italia Casi Totali
fig4 = px.choropleth(
    df_prov_map, 
    geojson='https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson', 
    locations='Province', 
    color='Total Cases', 
    color_continuous_scale='Reds', 
    featureidkey='properties.prov_istat_code_num', 
    animation_frame='Date', 
    range_color=(0, max(df_prov_map['Total Cases'])))
fig4.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig4.update_geos(fitbounds="locations", visible=False)

app = dash.Dash(__name__,
                meta_tags = [{
                    'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minumum-scale=0.5,'
                }]
                )
server = app.server

app.title = "Dashboard Dati Covid-19 Puglia"

#########################
######## LAYOUTS ########
#########################

app.layout = html.Div(children=[

    html.Center(html.H1(children='Epidemia di Coronavirus in Puglia')),

    html.Center(html.Div(children="Questa è un'applicazione per la visualizzazione dei dati sanitari in Puglia e nelle sue Provincie.")),

    html.Center(html.Div(children="Fonte Dati: Protezione Civile Italiana (Repository GitHub)")),

    html.Center(html.Div(children="Autore: Fonz0")),

    html.Div(children=[
        # Layout Province Puglia
        html.Center(html.H2(children='Dati Province')),

        html.Label('Seleziona la Provincia:'),
        
        dcc.Dropdown(id = "provincia",
                    options=[{"label": i, "value" : i} for i in ['Bari', 'Barletta-Andria-Trani', 'Brindisi', 'Foggia', 'Lecce', 'Taranto']],
                    value='Taranto'),

        dcc.Graph(id='grafico-province')
        ]),

    html.Div(children=[
        # Layout Regione Puglia
        html.Center(html.H2(children='Dati Regione')),

        html.Label('Seleziona Dato da mostrare:'),
        dcc.Dropdown(id = "dato_di_interesse",
                    options=[{"label": i, "value" : i} 
                    for i in df_puglia.drop(['denominazione_regione','lat', 'long', 'note_test', 'note_casi'], axis=1).columns],
                    value=['totale_positivi'],
                    multi=True),

        dcc.Graph(id='grafico-regione')]),
    
    html.Div(children=[
        # Layout Italia
        html.Center(html.H2(children='Dati a livello Nazionale: Italia')),

        html.Label('Seleziona Dato da mostrare:'),
        dcc.Dropdown(id = "dato_di_interesse_italia",
                    options=[{"label": i, "value" : i} for i in df_italia.drop(['stato', 'note_test', 'note_casi'], axis=1).columns],
                    value=['totale_positivi'],
                    multi=True),

        dcc.Graph(id='grafico-italia')]),

    html.Div(children=[
        # Layout Mappa Italia
        html.Center(html.H2(children='Dati Italia: Mappa')),
 
        dcc.Graph(id='grafico-italia-mappa', figure=fig4)])
    ])

#########################
####### CALLBACKS #######
#########################

# Callback per update Grafico Province
@app.callback(
    Output('grafico-province', 'figure'),
    Input("provincia", 'value'))
def update_figure_1(provincia):
    df = pd.DataFrame([df_province[provincia], df_province[provincia].diff()], index=["Totale Casi", "Variazione Casi"]).T
    fig1 = px.line(df, labels={'x':'DATA'}, log_y=True)
    fig1.update_layout(legend_title='', transition_duration=1000)
    return fig1

# Callback per update Grafico Regione.
@app.callback(
    Output('grafico-regione', 'figure'),
    [Input("dato_di_interesse", 'value')])
def update_figure_2(dato_di_interesse):
    title = ""
    for i in dato_di_interesse:
        title = title + i + " / "
    title = title[:-3]
    
    fig2 = px.line(df_puglia[dato_di_interesse], log_y=True)
    fig2.update_layout(legend_title="Puglia", transition_duration=1000)
    return fig2

# Callback per update Grafico Italia.
@app.callback(
    Output('grafico-italia', 'figure'),
    [Input("dato_di_interesse_italia", 'value')])
def update_figure_3(dato_di_interesse_italia):
    title = ""
    for i in dato_di_interesse_italia:
        title = title + i + " / "
    title = title[:-3]
    
    fig3 = px.line(df_italia[dato_di_interesse_italia], log_y=True)
    fig3.update_layout(legend_title="Puglia", transition_duration=1000)
    return fig3

# Lauch App-Server and Browser-Web.
if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=True)
