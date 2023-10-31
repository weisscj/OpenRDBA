# -*- coding: utf-8 -*-

# import modules
import os
import sys
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
from pathlib import Path

# Working directory setzen
sys.path.append(str(Path(__file__).parent.parent.resolve()))
path = os.getcwd()
print("Working directory: %s\n" %path)

# config importieren
from config.config import *

# activate seaborn
sns.set()

# Warnungen deaktivieren
pd.options.mode.chained_assignment = None  # default='warn'

if len(sys.argv) == 2:
    input_data = sys.argv[1]
else:
    #input_data = input("Geben Sie den Pfad für Ihren Datensatz an: ")
    input_data = '../data/data.pkl'

def import_data():
    ### Daten Importieren
    print('******************** Datenimport ********************')
    print("Importiere Datensatz. Dies kann eine Weile dauern...")
    # Daten importieren
    try:
        df = pd.read_pickle(input_data)
    except FileNotFoundError:
        print(f"Error: Die Datei {input_data} konnte nicht importiert werden.")
        sys.exit(1)
    
    # GeoDataFrame erzeugen
    gdf = gpd.GeoDataFrame(df,
        geometry = gpd.points_from_xy(df[col_einsatz_lon], df[col_einsatz_lat]), 
        crs = 'EPSG:4326')
    print('Datenimport erfolgreich.\n')
    print('Größe Datensatz: ' + str(df.shape) + '\n')
    return gdf

def import_regions():
    '''Docstring'''

    print('Verwaltungseinheiten werden importiert. Dies kann eine Weile dauern...')
    try:
        gdf = gpd.read_file('../data/LAU/LAU_RG_01M_2020_4326.geojson')
    except FileNotFoundError:
        print(f"Error: Die Datei {input_data} konnte nicht importiert werden.")
        sys.exit(1)
    gdf = gdf.to_crs('EPSG:4326')

    # Spaltennamen umbenennen
    gdf['Name'] = gdf['LAU_NAME']               # Name
    gdf['Einwohner'] = gdf['POP_2020']          # Einwohner
    gdf['Einwohnerdichte'] = gdf['POP_DENS_2020']  # Einwohnerdichte
    gdf['Fläche [km2]'] = gdf['AREA_KM2']       # Fläche
    
    # nicht benötigte Spalten löschen
    gdf = gdf.drop('LAU_NAME', axis=1)      # Name
    gdf = gdf.drop('POP_2020', axis=1)      # Einwohner
    gdf = gdf.drop('POP_DENS_2020', axis=1) # Einwohnerdichte
    gdf = gdf.drop('AREA_KM2', axis=1)      # Fläche
    gdf = gdf.drop('CNTR_CODE', axis=1)     # Ländercode
    gdf = gdf.drop('YEAR', axis=1)          # Jahr
    gdf = gdf.drop('FID', axis=1)           # FID
    #gdf = gdf.drop('LAU_ID', axis=1)        # LAU_ID

    return gdf

def stats_rdb_hilfsfrist(gdf, year):
    '''Berechnung der Hilfsfrist für den gesamten Rettungsdienstbereich
    
    Parameter:
    gdf (geodataframe):
    year (int): Jahr für welches die Hilfsfrist berechnet werden soll
    '''

    # nur für Hilfsfrist relevante Grundstichwörter filtern (definiert in config.py)
    gdf = gdf.loc[gdf[col_grundstichwort].isin(gs_hf)]
    
    gdf = gdf[gdf[col_zeit_hilfsfrist].notna()]
    hf_gesamt = gdf.loc[(gdf[col_rdb] == rdb_name)]

    # Hilfsfrist codieren in True/False
    hilfsfrist_true  = hf_gesamt.loc[(gdf[col_hilfsfrist] == True)]

    # Einsätze mit eingehaltener Hilfsfrist berechnen und durch Gesamtanzahl Einsätze teilen
    stats_hf_gesamt = hf_gesamt.groupby(col_rdb)[col_einsatz_nr].agg(['count'])
    stats_hilfsfrist_true  = hilfsfrist_true.groupby(col_rdb)[col_einsatz_nr].agg(['count'])
    result = stats_hilfsfrist_true['count'] / stats_hf_gesamt['count'] * 100
    result = np.round(result, 2)
    result = result.iloc[0]

    # Ergebnis ausgeben
    print('Einsätze: ' + str(hf_gesamt[col_einsatz_nr].count()))
    print('Hilfsfrist: ' + str(result) + '%')
    print('Median: ' + str(np.round(hf_gesamt[col_zeit_hilfsfrist].median(), 2)))
    print('Mean: ' + str(np.round(hf_gesamt[col_zeit_hilfsfrist].mean(), 2)))
    print('std: ' + str(np.round(hf_gesamt[col_zeit_hilfsfrist].std(), 2)))
    print('90. Perzentil: ' + str(np.round(hf_gesamt[col_zeit_hilfsfrist].quantile(.90), 2)))
    print('95. Perzentil: ' + str(np.round(hf_gesamt[col_zeit_hilfsfrist].quantile(.95), 2)))
    print('')
    
    #fig, ax = plt.subplots(layout='constrained', figsize=(16, 8))
    ax = sns.boxplot(x=col_einsatz_ort, y=col_zeit_hilfsfrist, data=hf_gesamt, orient="v")
    for container in ax.containers:
        ax.bar_label(container)
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    ax.axhline(15)
    #hf_gesamt.boxplot(column="Hilfsfrist_Einsatz")
    #plt.show()
    

def stats_rdb_fremd(gdf, year):
    '''Berechnung der Summe aller fremden Einsätze und fremden Rettungsmittel'''

    print('Anteile Einsätze pro RDB und fremde EM im eigenen RDB')    

    ## Einsätze pro RDB
    gdf_rdb = gdf.groupby([col_rdb, col_grundstichwort])[col_einsatz_nr].agg(['count']) # Gruppieren nach RDB und Grundstichwort
    gdf_rdb['percent'] = gdf_rdb['count'].transform(lambda x: x / float(x.sum()))       # Prozent berechnen (dezimal)
    gdf_rdb['percent'] = np.round(gdf_rdb['percent'] * 100, 2)                          # Prozent berechnen (Prozent + runden)
    # Ergebnisse speichern
    file = '../output/RDB/EM_nach_RDB_' + str(year) + '.csv'        # Outputdatei Name
    gdf_rdb.to_csv(file)                                                            # Ergebnisse speichern 
    print('>> Statistiken in ' + file + ' gespeichert.')

    ## Einsätze nach EM Herkunft
    gdf_rdb = gdf.groupby([col_em_rdb, col_grundstichwort])[col_einsatz_nr].agg(['count'])  # Gruppieren nach RDB und Grundstichwort
    gdf_rdb['percent'] = gdf_rdb['count'].transform(lambda x: x / float(x.sum()))   # Prozent berechnen (dezimal)
    gdf_rdb['percent'] = np.round(gdf_rdb['percent'] * 100, 2)                      # Prozent berechnen (Prozent + runden)
    # Ergebnisse speichern
    file = '../output/RDB/Einsatz_nach_RDB_' + str(year) + '.csv'   # Outputdatei Name
    gdf_rdb.to_csv(file)                                                            # Ergebnisse speichern
    print('>> Statistiken in ' + file + ' gespeichert.')

    # Idee Entwicklung: Bilanz berechnen

def stats_kommune(gdf):
    '''Statistiken für Kommunen berechnnen und als geodataframe zurückgeben'''

    # eigenen RDB filtern
    gdf = gdf.loc[gdf[col_rdb] == rdb_name]

    # Regionen importieren
    gdf_regions = gdf_regions_global.copy()

    # Anzahl Einsätze
    gdf_ = gdf.groupby('LAU_ID')[col_einsatz_nr].agg(['count'])                                 # Gruppieren nach LAU_ID und Anzahl Einsätze zählen
    gdf_['Einsätze_gesamt'] = gdf_['count']                                                     # Umbenennen
    gdf_ = gdf_.drop('count', axis=1)                                                           # Spalte löschen
    gdf_regions = pd.merge(gdf_regions, gdf_ , left_on='LAU_ID', right_index=True, how='outer') # merge Einsätze mit Kommunen
    gdf_regions['Einsätze_pro_1000_Einwohner'] = np.round(gdf_regions['Einsätze_gesamt'] / (gdf_regions['Einwohner'] / 1000), 2)    # Anzahl Einsätze pro 1000 Einwohner [Anzahl]
    
    # Regionen mit weniger als 25 Einsätzen löschen, erforderlich um fehlerhafte angrenzende Gebiete zu löschen
    gdf_regions = gdf_regions[gdf_regions['Einsätze_gesamt'] > 25]                              # Regionen mit weniger als 25 Einsätzen löschen

    # Fehleinsätze [%] berechnen
    gdf_ = gdf[gdf[col_fehleinsatz] == True]                                                    # Fehleinsätze filtern (nur Fehleinsatz = True verwenden)
    gdf_ = gdf_.groupby('LAU_ID')[col_einsatz_nr].agg(['count'])                                # Gruppieren nach LAU_ID und Anzahl Einsätze zählen
    gdf_['Fehleinsätze'] = gdf_['count']                                                        # Spalte umbenennen
    gdf_ = gdf_.drop('count', axis=1)                                                           # Spalte löschen
    gdf_regions = pd.merge(gdf_regions, gdf_ , left_on='LAU_ID', right_index=True, how='outer') # MERGE
    gdf_regions = gdf_regions[gdf_regions['GISCO_ID'].notna()]                                  # 
    gdf_regions['Fehleinsätze [%]'] = (np.round((gdf_regions['Fehleinsätze'] / gdf_regions['Einsätze_gesamt']) * 100, 2)).astype(int)   # Fehleinsätze in Prozent berechnen und runden
    gdf_regions['Fehleinsätze_pro_1000_Einwohner'] = np.round(gdf_regions['Fehleinsätze'] / (gdf_regions['Einwohner'] / 1000), 2)       # Anzahl Fehleinsätze pro 1000 Einwohner [Anzahl]

    # Gesamtzahl auswertbare Einsätze Hilfsfrist bestimmten und Hilfsfrist berechnen
    gdf_hf = gdf.loc[gdf[col_grundstichwort].isin(gs_hf)]                                       # nur für Hilfsfrist relevante Grundstichwörter filtern (definiert in config.py)
    gdf_hf  = gdf_hf[gdf_hf[col_zeit_hilfsfrist].notna()]                                       # Einsätze löschen, welche nicht für die Hilfsfristauswertung verwendet werden können
    gdf_hf_gesamt = gdf_hf.copy()                                                               # dataframe alle Einsätze erstellen
    gdf_hf_false  = gdf_hf.loc[(gdf_hf[col_hilfsfrist] == False)]                               # dataframe Hilfsfristüberschreitungen erstellen
    gdf_hf_gesamt = gdf_hf_gesamt.groupby('LAU_ID')[col_einsatz_nr].agg(['count'])              # Gruppieren nach LAU_ID und Anzahl Einsätze zählen (Einsätze gesamt)
    gdf_hf_false  = gdf_hf_false.groupby('LAU_ID')[col_einsatz_nr].agg(['count'])               # Gruppieren nach LAU_ID und Anzahl Einsätze zählen (Hilfsfristüberschreitungen)
    gdf_hf_gesamt['Einsätze_HF_gesamt'] = gdf_hf_gesamt['count']                                # Spalte umbenennen (Einsätze gesamt)
    gdf_hf_false['Hilfsfristüberschreitungen'] = gdf_hf_false['count']                          # Spalte umbenennen (Hilfsfristüberschreitungen)
    gdf_hf_gesamt = gdf_hf_gesamt.drop('count', axis=1)                                         # Spalte löschen (Einsätze gesamt)
    gdf_hf_false = gdf_hf_false.drop('count', axis=1)                                           # Spalte löschen (Hilfsfristüberschreitungen)
    gdf_regions = pd.merge(gdf_regions, gdf_hf_gesamt , left_on='LAU_ID', right_index=True, how='outer')    # merge Einsätze gesamt mit Kommunen
    gdf_regions = pd.merge(gdf_regions, gdf_hf_false , left_on='LAU_ID', right_index=True, how='outer')     # merge Hilfsfristüberschreitungen mit Kommunen
    gdf_regions = gdf_regions[gdf_regions['GISCO_ID'].notna()]                                  #
    gdf_regions['Hilfsfrist_[%]'] = (np.round((((gdf_regions['Hilfsfristüberschreitungen'] / gdf_regions['Einsätze_HF_gesamt']) * (-1) + 1) * 100), 2)).astype(int)  # Hilfsfrist in Prozent berechnen und runden

    # Kommunen mit berechnenen Statistiken als geodataframe zurückgeben
    return gdf_regions

def save_map(data, year, column_name='Hilfsfrist [%]'):
    '''Karte generieren und als html Dokument speichern
    
    Paramter:
    data (geodataframe): Datensatz
    year (int): Jahr für welches die Karte erstellt werden soll (wird für Dateinamen benötigt)
    column_name (str): Spalte die als Layer verwendet werden soll
    '''

    # Karte erstellen
    m = data.explore(
        column=column_name,                 # Choropletekarte basierend auf Spalte erstellen
        scheme="naturalbreaks",             # schema 'naturalbreaks' verwenden
        legend=True,                        # Legende anzeigen
        legend_kwds=dict(colorbar=False),   # keine Colorbar verwenden
        name=column_name,                   # Name des Layers
    )
    folium.LayerControl().add_to(m)         # layer control zur Karte hinzufügen

    # Karte speichern
    output_file = '../output/Kommunen/stats_' + str(year) + '_' + column_name + '.html'    # Dateiname
    m.save(output_file) # Karte als HTML Dokument speichern                             # Datei speichern
    print('>> Karte ' + output_file + ' gespeichert.')                                  # Ausgabe in Terminal

def stats_pop_unterversorgt(df):
    '''Potenziell unterversorgte Bevölkerung berechnen und in Konsole ausgeben.'''

    print('Potenziell unterversorgte Bevölkerung wird berechnet...')

    # Variablen initialisieren
    pop_gesamt = 0      # Einwohner gesamt
    pop_versorgt = 0    # Einwohner versorgt
    pop_unter = 0       # Einwohner unterversorgt

    # über alle Zeilen iterieren und abhängig ob unter oder über Hilfsfrist die Einwohner addieren
    for index, row in df.iterrows():
        if row['Hilfsfrist_[%]'] < 95:          # Hilfsfrist unterschritten
            pop_unter += row['Einwohner']           # Einwohner addieren (unterversorgt)
        else:                                   # Hilfsfrist eingehalten
            pop_versorgt += row['Einwohner']        # Einwohner addieren (versorgt)
        pop_gesamt += row['Einwohner']          # Einwohner addieren (gesamt)
    
    # Bevölkerung gesamt
    print('Einwohner gesamt: ' + str(pop_gesamt))

    # Bevölkerung versorgt
    pop_prozent = np.round(((pop_versorgt / pop_gesamt) * 100), 2)  # Prozentualen Anteil der unterversorgten Bevölkerung berechnen
    print('Einwohner versorgt: ' + str(pop_versorgt))               # Ausgabe in Terminal
    print('Einwohner versorgt [%]: ' + str(pop_prozent))            # Ausgabe in Terminal
    
    # Bevölkerung unterversorgt
    pop_prozent = np.round(((pop_unter / pop_gesamt) * 100), 2)     # Prozentualen Anteil der unterversorgten Bevölkerung berechnen
    print('Einwohner unterversorgt: ' + str(pop_unter))             # Ausgabe in Terminal
    print('Einwohner unterversorgt [%]: ' + str(pop_prozent))       # Ausgabe in Terminal

def calc_difference(gdf_begin, gdf_end, col_old, col_new):
    '''Differenz zwischen zwei dataframes berechnen und in neue Spalte speichern
    
    Parameter:
    gdf_begin (geodataframe): Datensatz zu Beginn des Zeitraums
    gdf_end (geodataframe): Datensatz am Ende des Zeitraums
    col_old (str): Spalte die differenziert werden soll
    col_new (str): Name der neuen Spalte
    '''

    gdf = gdf_end.copy()
    gdf[col_new] = gdf_end[col_old] - gdf_begin[col_old]
    gdf[col_new] = gdf[col_new].astype(int)
    #gdf = gdf.drop(col_old, axis=1)

    return gdf

def save_csv(gdf, year, column_name=''):
    '''GeoDataFrame als csv speichern'''

    gdf = gdf.drop('geometry', axis=1)                                          # Geometriespalte löschen
    file = '../output/Kommunen/stats_' + str(year) + '_' + column_name + '.csv'    # Dateiname
    gdf.to_csv(file)                                                            # Ergebnisse speichern
    print('>> Statistiken in ' + file + ' gespeichert.')                        # Ausgabe in Terminal

def save_gpkg(gdf, year, column_name=''):
    '''GeoDataFrame als gpkg speichern'''

    file = '../output/Kommunen/stats_' + str(year) + '_' + column_name + '.gpkg'   # Dateiname
    gdf.to_file(file, driver="GPKG")                                            # Ergebnisse speichern
    print('>> Layer in ' + file + ' gespeichert.')                              # Ausgabe in Terminal

def main():
    '''main function'''

    # Daten importieren
    data = import_data()

    # Kommunen importieren
    global gdf_regions_global
    gdf_regions_global = import_regions()
    print('')

    # nur Grundstichwörter der Notfallrettung filtern (definiert in config.py)
    data = data.loc[data[col_grundstichwort].isin(gs_nr)]

    # Alle Jahre aus Datensatz extrahieren
    years = data[col_ts_alarm].dt.year.unique()

    # erstes und letztes Jahr in Datensatz bestimmen
    year_begin = years[0]
    year_end = years[-1]

    # über alle Jahre iterieren
    for year in years:
        print('******************** Jahr: ' + str(year) + ' ********************')
        data_year = data.loc[data[col_ts_alarm].dt.year == year]

        ### Berechnung Hilfsfrist für gesamten RDB
        stats_rdb_hilfsfrist(data_year, year)
        
        # Statistiken für Kommunen berechnen
        data_regions = stats_kommune(data_year)
        
        # Berechnung unterversorgte Bevölkerung
        stats_pop_unterversorgt(data_regions)
        print('')
        
        # Anteile fremde EM und Einsätze in fremden RDB
        stats_rdb_fremd(data_year, year)
        print('')

        # Ergebnisse speichern (Karten, csv und gpkg)
        print('Ergebnisse werden gespeichert...')
        save_map(data_regions, year, 'Einsätze_gesamt')                 # Karte Einsätze gesamt
        save_map(data_regions, year, 'Einsätze_pro_1000_Einwohner')     # Karte Einsätze pro 1000 Einwohner
        save_map(data_regions, year, 'Fehleinsätze_pro_1000_Einwohner') # Karte Fehleinsätze pro 1000 Einwohner
        save_map(data_regions, year, 'Hilfsfrist_[%]')                  # Karte Hilfsfrist
        save_csv(data_regions, year)                                    # csv speichern
        save_gpkg(data_regions, year)                                   # gpkg speichern
        print('')

        # Raum-zeitliche Differenzen berechnen
        # beim letzten durchlauf der for Schleife wird die Differenz zwischen dem ersten Jahr und dem letzen Jahr im Datensatz berechnet.
        if year == year_begin:
            data_regions_begin = data_regions
        elif year == year_end:
            data_regions_end = data_regions

            print('******************** Raum-zeitliche Veränderungen ********************')

            # Veränderung Einsätze gesamt
            col = 'Einsätze_gesamt_Veränderung'
            data_regions_temp = calc_difference(data_regions_begin, data_regions_end, 'Einsätze_gesamt', col)
            print('Veränderung Einsätze gesamt')
            save_map(data_regions_temp, year, col)
            save_csv(data_regions_temp, year, col)
            save_gpkg(data_regions_temp, year, col)
            print('')

            # Veränderung Einsätze pro 1000 Einwohner
            col = 'Einsätze_pro_1000_Einwohner_Veränderung'
            data_regions_temp = calc_difference(data_regions_begin, data_regions_end, 'Einsätze_pro_1000_Einwohner', col)
            print('Veränderung Einsätze pro 1000 Einwohner')
            save_map(data_regions_temp, year, col)
            save_csv(data_regions_temp, year, col)
            save_gpkg(data_regions_temp, year, col)
            print('')

            # Veränderung Fehleinsätze pro 1000 Einwohner
            col = 'Fehleinsätze_pro_1000_Einwohner_Veränderung'
            data_regions_temp = calc_difference(data_regions_begin, data_regions_end, 'Fehleinsätze_pro_1000_Einwohner', col)
            print('Veränderung Fehleinsätze pro 1000 Einwohner')
            save_map(data_regions_temp, year, col)
            save_csv(data_regions_temp, year, col)
            save_gpkg(data_regions_temp, year, col)
            print('')

            # Veränderung Hilfsfrist
            col = 'Hilfsfrist_Veränderung'
            data_regions_temp = calc_difference(data_regions_begin, data_regions_end, 'Hilfsfrist_[%]', col)
            print('Veränderung Hilfsfrist')
            save_map(data_regions_temp, year, col)
            save_csv(data_regions_temp, year, col)
            save_gpkg(data_regions_temp, year, col)
            print('')

    input('\nDrücken Sie eine beliebige Taste zum Beenden...')

if __name__ == '__main__':
    main()