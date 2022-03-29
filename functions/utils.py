import pandas as pd

def retrieve_data():
    '''
    Function to retrieve datasets from GitHub repository of "Protezione Civile Italiana"
    '''
    url_italia = r"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    url_regioni_ita = r"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    url_provincie_ita = r"https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    
    df_italia = pd.read_csv(url_italia)
    df_italia.drop("note", axis=1, inplace=True)

    df_regioni = pd.read_csv(url_regioni_ita)
    df_regioni.drop(["stato",
                    "codice_regione",
                    "note",
                    "codice_nuts_1",
                    "codice_nuts_2"],
                    axis=1,
                    inplace=True)

    df_province = pd.read_csv(url_provincie_ita)
    df_province.drop(["stato", 
                    "codice_regione", 
                    "codice_provincia", 
                    "denominazione_regione",
                    "sigla_provincia",
                    "note",
                    "codice_nuts_1",
                    "codice_nuts_2",
                    "codice_nuts_3"],
                    axis=1, 
                    inplace=True)
    
    df_province.drop(df_province[(df_province["denominazione_provincia"] == "In fase di definizione/aggiornamento") | 
                                 (df_province["denominazione_provincia"] == "Fuori Regione / Provincia Autonoma")].index,
                                 inplace=True)
    df_province_coord = df_province[["denominazione_provincia", "lat", "long"]].drop_duplicates()
    df_province.drop(["lat", "long"], axis=1, inplace=True)
    df_province = df_province.pivot("denominazione_provincia", "data").T.loc["totale_casi"]
    df_province.index = pd.to_datetime(df_province.index)
    
    # Read Data for Italy Map Viewer
    df_prov_map = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
    # Drop useless colums
    df_prov_map.drop(columns=['stato', 'codice_regione', 'denominazione_regione','sigla_provincia', 'lat', 'long', 'note', 'codice_nuts_1', 'codice_nuts_2', 'codice_nuts_3'], axis=1, inplace=True)
    # Drop useless rows 
    df_prov_map = df_prov_map[df_prov_map['denominazione_provincia'] != 'In fase di definizione/aggiornamento']
    # Columns manipulation
    df_prov_map = df_prov_map.rename(columns={'codice_provincia': 'Province'})
    df_prov_map = df_prov_map.rename(columns={'totale_casi': 'Total Cases'})
    df_prov_map['Date'] = pd.to_datetime(df_prov_map['data'], format="%Y-%m-%d")
    df_prov_map['Date'] = df_prov_map['Date'].dt.strftime('%Y-%m-%d')

    print(df_italia)
    print(df_regioni)
    print(df_province)
    print(df_province_coord)
    print(df_prov_map)

    return df_italia, df_regioni, df_province, df_province_coord, df_prov_map