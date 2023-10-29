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
    print("Importiere Datensatz. Dies kann eine Weile Minuten dauern...")
    df = pd.read_pickle(input_data)
    # GeoDataFrame erzeugen
    gdf = gpd.GeoDataFrame(df,
        geometry = gpd.points_from_xy(df[col_einsatz_lon], df[col_einsatz_lat]), 
        crs = 'EPSG:4326')
    print('Datenimport erfolgreich.\n')
    print('Größe Datensatz: ' + str(df.shape))
    return gdf

def import_regions(df_):
    '''Docstring'''

    print('Regionen werden importiert...')
    gdf = gpd.read_file('../data/region/regions.gpkg')
    gdf = gdf.to_crs(df_.crs)

    return gdf

def q95(x):
    '''95. Perzentil berechnen und zurückeben'''
    return x.quantile(0.95)

def q90(x):
    '''90. Perzentil berechnen und zurückeben'''
    return x.quantile(0.90)

def get_years(df):
    '''Alle im Datensatz enthaltenen Jahre in Liste speichern und zurückgeben'''

    global list_years
    list_years = df[col_ts_alarm].dt.year.unique()
    list_years = list_years.tolist()
    list_years.sort()
    return list_years

def get_em_typ(df):
    '''Alle im Datensatz enthaltenen Einsatzmittel in Liste speichern und zurückgeben'''

    em_typ = df[col_em_typ].unique()
    em_typ = em_typ.tolist()
    em_typ.sort()
    return em_typ

def save_results(gdf, m, output_file):
    '''Speicherung der Ergebnisse'''

    file = path + output_file

    # Ergebnisse speichern
    m.save('../output/' + output_file + '.html')                                    # Karte
    print('Karte gespeichert unter: ' + '../output/' + output_file + '.html')           # Ausgabe in Konsole
    gdf.to_csv('../output/' + output_file + '.csv', sep=';')                        # csv
    print('CSV gespeichert unter: ' + '../output/' + output_file + '.csv')              # Ausgabe in Konsole
    gdf.to_file('../output/' + output_file + '.gpkg', driver='GPKG')                # GeoPackage
    print('GeoPackage gespeichert unter: ' + '../output/' + output_file + '.gpkg')      # Ausgabe in Konsole

    input('\nDrücken Sie eine beliebige Taste um zum Hauptmenü zurückzukehren...')

def stats_versorgungszeit(gdf, gdf_regions, column, gs_sw, bins):
    '''Versorgungszeiten berechnen und Karte erstellen'''

    print('Versorgungszeiten werden berechnet...')

    # Filtern nach Stichwort oer Grundstichwort
    if column == col_grundstichwort:
        gdf_regions['Grundstichwort'] = gs_sw               # Stichwort/ Grundstichwort als Info hinzufügen
        gdf = gdf.loc[(gdf[col_grundstichwort] == gs_sw)]   # Datensatz nach Grundstichwort filtern
    elif column == col_stichwort:
        gdf_regions['Stichwort'] = gs_sw                    # Stichwort/ Grundstichwort als Info hinzufügen
        gdf = gdf.loc[(gdf[col_stichwort] == gs_sw)]        # Datensatz nach Stichwort filtern

    # Filtern
    gdf = gdf.loc[gdf[col_rdb] == rdb_name]

    # Spatial JOIN
    gdf_ = gdf.sjoin(gdf_regions, how='left')
    gdf_ = gdf_.drop('index_right', axis=1)   

    # Median berechnen
    result = gdf_.groupby('area_id')[col_zeit_gesamt_pat].agg(['median'])
    gdf_regions = pd.merge(gdf_regions, result , left_on='area_id', right_index=True, how='outer')

    # Deskriptive Statistik berechnen
    result = gdf_.groupby('area_id')[col_zeit_gesamt_pat].describe()
    gdf_regions = pd.merge(gdf_regions, result , left_on='area_id', right_index=True, how='outer')
    
    # Regionen mit nan values entfernen
    gdf_regions = gdf_regions[gdf_regions['count'].notna()]

    # Karte erstellen
    m = gdf_regions.explore(
        column='median',                    # Spalte, die für die Färbung verwendet wird
        scheme="user_defined",             # Klasseneinteilung //user_defined 
        classification_kwds={'bins': bins}, # Klassengrenzen definieren
        legend=True,                        # Legende anzeigen
        legend_kwds={'colorbar': False},    # Keine Farbskala in der Legende anzeigen
        cmap='Reds',                        # Farbschema
    )

    # Ergebnisse speichern
    save_results(gdf_regions, m, 'Versorgungszeit/versorgungszeit_' + column + '_' + gs_sw)


def stats_erreichbarkeit(gdf, gdf_regions, em_type):
    '''Erreichbarkeiten berechnen und Karte erstellen'''

    print('Statistiken für Hilfsfristen werden erstellt...')

    # Filterung
    gdf = gdf.loc[gdf[col_rdb] == rdb_name]     # nur eigenen RDB betrachten
    gdf = gdf.loc[gdf[col_status_alarm] == '2'] # nur Fahrzeuge aus Status 2 betrachten
    gdf = gdf[gdf[col_zeit_hilfsfrist_em].notna()] # nur auswertbare Einsätze betrachten
    gdf = gdf.loc[gdf[col_zeit_hilfsfrist_em] != np.nan]
    
    # Listen erstellen
    wachen = gdf[col_em_wache].unique().tolist()        # Liste mit Wachen generieren
    regions = gdf_regions['area_id'].unique().tolist()  # Liste mit ids der Regionen generieren

    # Spatial JOIN um Datensatz mit Einsätzen Informationen über die Regionen zu geben
    gdf = gdf.sjoin(gdf_regions, how='left')    # JOIN
    gdf = gdf.drop('index_right', axis=1)       # Spalte löschen
    
    # Leere Liste für Ergebnisse erstellen
    frames = []

    for region in regions:
        gdf_ = gdf.loc[gdf['area_id'] == region]
        gdf_region = gdf_regions.loc[gdf_regions['area_id'] == region]
        # häufigstes Einsatzmittel identifizieren
        gdf_stats = gdf_.groupby(col_em_wache)[col_zeit_hilfsfrist_em].agg(['count'])
        gdf_stats.sort_values(by=['count'], inplace=True, ascending=False)

        # Diese Funktion soll für jede Region die drei am häufigsten disponierten Einsatzmittel finden
        # Für jedes Einsatzmittel werden dann die Statistiken count, median und p95 berechnet
        i = 1
        for index, row in gdf_stats[:3].iterrows():
            # index = Einsatzmittel
            # row = Einsatz

             # EM_Wache filtern
            gdf_wache = gdf_.loc[gdf_[col_em_wache] == index]  

            # Einsatzmittel bestimmen:
            col = str(i) + '. EM:'
            gdf_region[col] = index

            # Anzahl Notfalleinsätze
            col = str(i) + ': Einsätze [Anzahl]'
            gdf_region[col] = gdf_wache[col_einsatz_nr].count()

            # Anteil Notfalleinsätze
            col = str(i) + ': Anteil Einsätze [%]'
            gdf_region[col] = np.round((gdf_wache[col_einsatz_nr].count() / gdf_[col_einsatz_nr].count() * 100), 2)

            # HF median [min]
            col = str(i) + ': HF median [min]'
            gdf_region[col] = np.round(gdf_wache[col_zeit_hilfsfrist_em].median(), 2)

            # HF p95 [min]
            col = str(i) + ': HF p95 [min]'
            gdf_region[col] = np.round(gdf_wache[col_zeit_hilfsfrist_em].quantile(0.95), 2)

            # Anfahrt median [min]
            col = str(i) + ': Anfahrt median [min]'
            gdf_region[col] = np.round(gdf_wache[col_zeit_anfahrt].median(), 2)

            # Anfahrt p95 [min]
            col = str(i) + ': Anfahrt p95 [min]'
            gdf_region[col] = np.round(gdf_wache[col_zeit_anfahrt].quantile(0.95), 2)

            i += 1

        frames.append(gdf_region)
    result = pd.concat(frames)

    # Karte erstellen
    m = result.explore(
        column='1. EM:',                    # make choropleth based on "POP2010" column
        scheme="naturalbreaks",             # use mapclassify's natural breaks scheme
        legend=True,                        # show legend
        legend_kwds=dict(colorbar=False),   # do not use colorbar
        name="Test",                        # name of the layer in the map
    )
    folium.LayerControl().add_to(m)         # use folium to add layer control

    # Ergebnisse speichern
    output_path = 'Fahrzeit/stats_fahrzeit_' + em_type
    save_results(result, m, output_path)

def clear_screen():
    '''Konsole leeren (abhängig vom Betriebssystem)'''

    if os.name == 'posix':      # für Linux/Unix
        _ = os.system('clear')
    else:                       # für Windows
        _ = os.system('cls')

def print_menu():
    '''Hauptmenü'''

    clear_screen()  # Konsole leeren
    print('******************** Hauptmenü ********************')
    print('1 - Fahrzeitanalyse gesamt')
    print('2 - Fahrzeitanalyse für Rettungswache')
    print('3 - Versorgungszeit für Grundstichwort')
    print('4 - Versorgungszeit für Stichwort')
    print('')
    print('99 - Beenden')

def select_year(df):
    '''Docstring'''

    print('Welches Jahr möchten Sie auswerten? Geben Sie nichts ein, wenn Sie alle Jahre verwenden möchten.')
    print('vorhandene Jahre: ' + str(list_years))
    year = input('>> ')
    try:
        df = df.loc[df[col_ts_alarm].dt.year == int(year)]
    except:
        pass
    print('')
    return df

def select_em_typ(df):
    '''Einsatzmitteltyp auswählen'''

    print('Welchen Einsatzmitteltyp möchten Sie auswerten?')
    print('vorhandene Einsatzmitteltypen: ' + str(list_em_typ))
    em_typ = input('>> ')
    try:
        df = df.loc[df[col_em_typ] == em_typ]
    except:
        print('Fehler bei der Eingabe')
        sys.exit(0)
    print('')
    return df, em_typ

def select_gs_single(df):
    '''Grundstichwort auswählen'''

    print('Welches Grundstichwort möchten Sie auswerten?')
    print('vorhandene Grundstichwörter: ' + str(list_gs))
    gs = input('>> ')
    try:
        df = df.loc[df[col_grundstichwort] == gs]
    except:
        print('Fehler bei der Eingabe')
        sys.exit(0)
    print('')
    return df, gs

def select_gs_multiple(df):
    '''Grundstichwort auswählen'''

    print('Welche Grundstichwörter möchten Sie auswerten? Geben Sie die Grundstichwörter getrennt durch ein Komma und ohne Leerzeichen ein [GS1,GS2]')
    print('vorhandene Grundstichwörter: ' + str(list_gs))
    gs = input('>> ')
    try:
        df = df.loc[df[col_grundstichwort].isin(gs.split(','))]
    except:
        print('Fehler bei der Eingabe')
        sys.exit(0)
    print('')
    return df

def select_sw_single(df):
    '''Stichwort auswählen'''

    print('Welches Stichwort möchten Sie auswerten? Geben Sie die Stichwörter getrennt durch ein Komma und ohne Leerzeichen ein [Stichwort1,Stichwort2]')
    print('vorhandene Stichwörter: ' + str(list_sw))
    sw = input('>> ')
    try:
        df = df.loc[df[col_stichwort] == sw]
    except:
        print('Fehler bei der Eingabe')
        sys.exit(0)
    print('')
    return df, sw

def select_sw_multiple(df):
    '''Stichwort auswählen'''

    print('Welches Stichwort möchten Sie auswerten?')
    print('vorhandene Stichwörter: ' + str(list_sw))
    sw = input('>> ')
    try:
        df = df.loc[df[col_stichwort].isin(sw.split(','))]
    except:
        print('Fehler bei der Eingabe')
        sys.exit(0)
    print('')
    return df

def select_em_wache(df, em_typ):
    '''Einsatzmittel, bzw. Wache auswählen'''

    temp = df.loc[df[col_em_typ] == em_typ]

    # Liste RDB erstellen
    list_rdb = temp[col_em_rdb].unique().tolist()

    # Multidimensionale Liste mit allen Wachen beasierend auf dem Rettungsdienstbereich erstellen
    list_wachen = []
    for rdb in list_rdb:
        list_wachen.append(temp.loc[temp[col_em_rdb] == rdb][col_em_wache].unique().tolist())

    print('Welches Rettungswache möchten Sie auswerten? In Datensatz gefundene Rettungswachen: ')
    for rdb in range(len(list_rdb)):
        print('RDB: ' + list_rdb[rdb])
        print(list_wachen[rdb])
    wache = input('>> ')
    try:
        df = df.loc[df[col_em_wache] == wache]
    except:
        print('Fehler bei der Eingabe')
        #break
    print('')
    return df

def select_bins():
    '''globale Liste mit Stichwörtern ändern'''

    bins = []
    bins_default = [0, 50, 60, 70]
    print('Im folgenden können Sie die Klassengrenzen für den Plot manuelle eingeben.')
    print('Geben Sie die Klassengrenzen getrennt durch ein Komma und ohne Leerzeichen ein [GS1,GS2]')
    print('> Geben Sie nichts ein und drücken Sie die Eingabetaste um die Standardwerte zu verwenden')
    print('')
    print('Standard: ' + str(bins_default))
    i = input('>> ')

    if i == '':
        bins = bins_default
    else:
        # Eingabe zu Liste hinzufügen
        for i in i.split(','):
            try:
                bins.append(float(i))
            except:
                pass
    return bins


def main():
    '''main function'''
    
    # Daten importieren
    data_ = import_data()           # Daten
    data = data_.copy()
    regions_ = import_regions(data) # Regionen

    # Liste mit allen Jahren erstellen
    global list_years
    list_years = get_years(data)

    # Liste mit allen Einsatzmitteltypen erstellen
    global list_em_typ                  # globale Variable deklarieren
    list_em_typ = get_em_typ(data)      # 

    while True:
        regions = regions_.copy()
        # nur Daten aus Liste mit Jahren nehmen
        # dies sollte noch in eine Unterfunktion/ Schleife verschoben werden
        data = data_.loc[data_[col_ts_alarm].dt.year.isin(list_years)]

        print_menu()        # Menü anzeigen
        x = input('>> ')    # Eingabe Konsole
        clear_screen()      # Konsole leeren

        # Programm beenden
        if x == '99':
            break

        # Fahrzeitanalyse gesamt
        elif x == '1':
            clear_screen()                              # Konsole leeren
            data = select_year(data)                    # Jahr auswählen
            data, em_typ = select_em_typ(data)          # EM Typ auswählen
            data = select_gs_multiple(data)             # Grundstichwörter auswählen
            stats_erreichbarkeit(data, regions, em_typ) # Analyse
            
        # Fahrzeitanalyse für Rettungswache
        elif x == '2':
            clear_screen()                              # Konsole leeren
            data = select_year(data)                    # Jahr auswählen
            data, em_typ = select_em_typ(data)          # EM Typ auswählen
            data = select_em_wache(data, em_typ)        # Rettungswache auswählen
            data = select_gs_multiple(data)             # Grundstichwörter auswählen
            stats_erreichbarkeit(data, regions, em_typ) # Analyse
        
        # Versorgungszeiten Grundstichwort
        elif x == '3':
            clear_screen()                                                  # Konsole leeren
            data = select_year(data)                                        # Jahr auswählen
            data, gs = select_gs_single(data)                               # Grundstichwörter auswählen

            bins = select_bins()                                    # Klassengrenzen definieren
            stats_versorgungszeit(data, regions, col_grundstichwort, gs, bins)    # Analyse

        # Versorgungszeiten Stichwörter
        elif x == '4':
            clear_screen()                                          # Konsole leeren
            data = select_year(data)                                # Jahr auswählen

            # Liste mit allen Stichwörter erstellen
            global list_sw
            list_sw = data[col_stichwort].unique().tolist()
            list_sw.sort()

            bins = select_bins()                                    # Klassengrenzen definieren
            data, sw = select_sw_single(data)                       # Grundstichwörter auswählen
            stats_versorgungszeit(data, regions, col_stichwort, sw, bins) # Analyse
        

if __name__ == '__main__':
  main()
