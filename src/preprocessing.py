# -*- coding: utf-8 -*-

# import modules
import sys
import os
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
from osgeo import ogr
from osgeo import osr

# Working directory setzen
sys.path.append(str(Path(__file__).parent.parent.resolve()))
path = os.getcwd()
print('Working directory: %s\n' %path)

# EPSG definieren
source = osr.SpatialReference()
source.ImportFromEPSG(4326)
target = osr.SpatialReference()
target.ImportFromEPSG(32632)
transform = osr.CoordinateTransformation(source, target)

# config importieren
from config.config import *

# Warnungen pandas ausschalten
pd.options.mode.chained_assignment = None  # default='warn'

if len(sys.argv) == 2:
    input_data = sys.argv[1]
else:
    input_data = input('Geben Sie den Pfad zu Ihrem Datensatz an: ')

def import_data():
    '''Datenimport'''
    print('******************** Datenimport ********************')
    print('Importiere Datensatz. Dies kann eine Weile Minuten dauern...')
    try:
        df = pd.read_csv(input_data, sep = ';')
    except FileNotFoundError:
        print(f"Error: Die Datei {input_data} konnte nicht importiert werden.")
        sys.exit(1)
    print('Erledigt. Größe Datensatz: ' + str(df.shape) + '\n')
    return df

def filter_value(df, input_file, col):
    '''Dataframe filtern auf Grundlage von Zellenwerten in spezfizierter Spalte. Zellenwerte werden aus Datei ausgelesen

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    input_file (str): Pfad zur Datei mit Zellenwerten nach denen gefiltert werden soll
    col (str): Spaltenname
    '''

    # neuen DataFrame erstellen mit Auswahlkriterium
    with open(input_file) as file:
        kriterium_liste = file.read().splitlines()

    df = df.loc[df[col].isin(kriterium_liste)]
    return df

def define_Stichwort(df, input_file):
    '''Stichwort Bezeichnungen und Grundstichwörter über Spalte Stichwörter definieren

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    input_file (str): Datei mit matching Tabelle
    '''

    file = open(input_file, 'r')
    lines = file.readlines()
    file.close()
    df[col_stichwort_bez] = '-'
    df[col_grundstichwort] = '-'
    list_filter = []
    for line in lines:
        line  = line.split(';')
        stichwort = line[0]
        stichwort_bez = line[1]
        grundstichwort = line[2].strip('\n')
        
        df[col_stichwort_bez].loc[df[col_stichwort] == stichwort] = stichwort_bez
        df[col_grundstichwort].loc[df[col_stichwort] == stichwort] = grundstichwort

        list_filter.append(stichwort)

    # Stichwörter herausfiltern die nicht in matching Datei sind
    df = df.loc[df[col_stichwort].isin(list_filter)]

    return df

def define_em_rdb(df, input_file):
    '''Namen von Rettungsdienstbereichen umschreiben und Filtern

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    input_file (str): Datei mit matching Tabelle
    '''

    file = open(input_file, 'r')
    lines = file.readlines()
    file.close()
    df = neue_spalte(df, col_em, col_em_rdb, ' ')   # Spalte erstellen
    list_filter = []
    for line in lines:
        line  = line.split(';')
        rdb_alt = line[0]
        rdb_neu = line[1].strip('\n')
        
        df[col_em_rdb].loc[df[col_em_rdb] == rdb_alt] = rdb_neu

        list_filter.append(rdb_neu)

    # RDB herausfiltern die nicht in matching Datei sind
    df = df.loc[df[col_em_rdb].isin(list_filter)]

    return df

def define_Wache_coord(df, input_file):
    '''Grundstichwörter definieren

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    input_file (str): 
    '''
    df[col_wache_lat] = np.nan
    df[col_wache_lon] = np.nan

    file = open(input_file, 'r')
    lines = file.readlines()
    for line in lines[1:]:
        line  = line.split(';')
        wache = line[0]
        lat = line[1]
        lon = line[2].strip('\n')
        df[col_wache_lat].loc[df[col_wache] == wache] = float(lat)
        df[col_wache_lon].loc[df[col_wache] == wache] = float(lon)
    df[col_wache_coord] = df.apply(create_col_coord, axis=1, args=(col_wache_lat, col_wache_lon))
    return df

def del_nanvalue(df, spalte):
    '''Alle Zeilen löschen die in einer gegebenen Spalte NaN Werte enthalten

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    spalte (str): 
    '''

    dif = df[col_id].count()
    df = df[df[spalte].notna()]
    dif = dif - df[col_id].count()
    print(str(dif) + ' Einsätze der Spalte ' + str(spalte) + ' wurden gelöscht')
    return df

def del_koordinaten(df, lat, lon):
    '''Koordinaten löschen

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    lat (float): Spalte mit lat Koordianten
    lon (float): Spalte mit lon Koordianten
    '''

    dif = df[col_id].count()
    df = df[df[lat].notna()]
    df = df[df[lon].notna()]
    dif = dif - df[col_id].count()
    print('%s Einsätze ohne Koordinaten wurden gelöscht' %dif)
    return df

def time_difference(df, col, a, b):
    '''Differenz zwischen zwei Zellwerten berechnen

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    col (str): Description of arg1
    a (datetime): Description of arg1
    b (datetime): Description of arg1
    '''

    df[col] = pd.to_timedelta(df[b] - df[a])                 # Zeitdelta berechnen
    df[col] = df[col].dt.total_seconds().astype(float)/60     # Zeitdelta in Minuten umwandeln (Dezimal Format)
    df[col] = round(df[col], 4)                               # auf zwei Nachkommastellen runden
    df = df.replace(0.0, np.nan)

    negativ = 0
    gesamt = 0

    for index, row in df.iterrows():
        if row[col] <= 0.0:
            negativ += 1
        gesamt += 1

    return df

def neue_spalte(df, col_alt, col_neu, parameter):
    '''Neue Spalte erstellen auf Grundlage des Wertes einer anderen Spalte

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    col_alt (str): Input Spalte
    col_neu (str): Output Spalte
    parameter (str): Parameter zum Aufteilen des strings in der übergebenen Spalte
    '''

    df[col_neu] = df[col_alt]

    # Position des Parameters finden und temporärte Spalte erstellen
    df['temp'] = df[col_neu].str.find(parameter)

    # Überprüfung, ob der Parameter im Text gefunden wurde, falls ja: string aufteilen
    df[col_neu] = df.apply(lambda x: x[col_neu][0:x['temp']] if x['temp'] >= 0 else x[col_neu], axis=1)

    # temporäre Spalte löschen
    df = df.drop('temp', axis=1)
    
    return df

def correct_coord(df, lat, lon):
    '''Formatierung der Koorindaten ändern. Komma wird zu Punkt

    Paramter:
    df (dataframe): Dataframe auf dem die Operation ausgeführt werden soll
    lat (string): Name der Spalte in der die lat Koordianten gespeichert sind
    lon (string): Name der Spalte in der die lon Koordianten gespeichert sind
    '''

    try:
        df[lat] = df[lat].str.replace(',', '.').astype(float)
        df[lon] = df[lon].str.replace(',', '.').astype(float)
    except Exception as Error:
        print(Error)
    
    return df

def create_col_coord(df, lat, lon):
    '''Spalte mit Punktgeometrie erzeugen aus den Spalten lat und lon

    Paramter:
    df (dataframe): Dataframe auf dem die Operation ausgeführt werden soll
    lat (string): Name der Spalte in der die lat Koordianten gespeichert sind
    lon (string): Name der Spalte in der die lon Koordianten gespeichert sind
    '''

    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(df[lat], df[lon])
    p.Transform(transform)

    return p.ExportToWkt()

def calculate_distance(df, col1, col2):
    '''Distanzberechnung (euklidisch) auf Grundlage zweiter Punkte vornehmen

    Paramter:
    df (dataframe): Dataframe auf dem die Operation ausgeführt werden soll
    col1 (string): Punkt 1 (Name der Spalte)
    col2 (string): Punkt 2 (Name der Spalte)
    '''

    p1 = ogr.CreateGeometryFromWkt(df[col1])
    p2 = ogr.CreateGeometryFromWkt(df[col2])
    dist = p1.Distance(p2)
    return dist

def calculate_speed(df, col_distance, col_time):
    ''''Durchschnittsgeschwindigkeiten berechnen

    Paramter:
    df (dataframe): Dataframe auf dem die Operation ausgeführt werden soll
    col_distance (string): Name der Spalte "Distanz"
    col_time (string): Name der Spalte "Anfahrtszeit"
    '''

    return (df[col_distance] / df [col_time])

def spatial_join(df):
    ''''
    Mit dieser Funktion werden dem übergebenen dataframe/ datensatz weitere Inforamtionen hinzugefügt.
    Dabei wird ein spatial join (räumliche Verknüpfung) zwischen dem Datensatz und weiteren Datensatz hergestellt.
    Die Ergebenisse sind Grundlage für die spätere Genrierung von Plots und Karten.

    Paramter:
    df (dataframe): Dataframe auf dem die Operation ausgeführt werden soll
    '''

    # Einsatz über spatial join dem entsprechenden Rettungsdienstbereich zuordnen.
    rdb = gpd.read_file('../data/rdb.gpkg')
    gdf_lau = gpd.read_file('../data/LAU/LAU_RG_01M_2020_4326.geojson')
    rdb = rdb.to_crs(df.crs)
    gdf_lau = gdf_lau.to_crs(df.crs)

    # Spatial Join um info über RDB hinzuzufügen
    gdf = df.copy()
    gdf = gdf.sjoin(rdb, how='left')
    gdf = gdf.drop('index_right', axis=1)

    # Spatial Join um info über Kommune hinzuzufügen
    gdf = gdf.sjoin(gdf_lau, how='left')
    gdf[col_einsatz_ort] = gdf['LAU_NAME']
    gdf = gdf.drop('CNTR_CODE', axis=1)
    gdf = gdf.drop('GISCO_ID', axis=1)
    gdf = gdf.drop('POP_2020', axis=1)
    gdf = gdf.drop('POP_DENS_2020', axis=1)
    gdf = gdf.drop('AREA_KM2', axis=1)
    gdf = gdf.drop('YEAR', axis=1)
    gdf = gdf.drop('FID', axis=1)
    gdf = gdf.drop('LAU_NAME', axis=1)
    gdf = gdf.drop('index_right', axis=1)

    return gdf

def save_stats(df_, col_list, name):
    '''Gruppiert die Einträge nach einer übergebenen Liste an Spaltennamen und speichert diese in Datei ab.

    Parameter:
    df_ (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    col_list (list): Liste mit Spaltennamen
    name (): Name für das zu speichernde Dokument
    '''

    # Kopie des Dateframes erstellen auf Grundlage der übergebenen Spalten
    df_ = df_[col_list].copy()
    # ersten Eintrag in Liste für die Ausgabe der Anzahl benutzen
    df_ = df_.groupby(col_list)[col_list[0]].count()
    # Ergebnisse in Datei speichern
    output_file = '../config/output_'+ str(name) +'.csv'
    df_.to_csv(output_file, sep=';')
    print(name + ' in Datei ' + output_file + ' gespeichert')

def calculate_hilfsfrist(df):
    '''
    Hilfsfrist berechnen. Gemäß den Baden-Württembergischen Vorgaben markiert das ersteintreffende
    Fahrzeig die Hilfsfrist. Diese Funktion sortiert den Datensatz nach Einsatznummer und Hilfsfrist und
    nimmt die schnellste Zeit als Hilfsfrist für den gesamten Einsatz. Um die Daten später weiter verarbeiten
    zu können, wird die Hilfsfrist bei einem EInsatzm mit mehreren Zeilen nur dem Einsatzmittel/ bzw. Auftrag
    mit der kleinsten Hilfsfriust zugeordnet (also dem Einsatzmittel, welches die Hilfsfrist markiert).
    Einsätze mit negativen Werten oder einer Hilfsfrist von über 60 Minuten werden nicht verwendet.
    Zusätzlich werden die theoretischen Hilfsfristen für jedes Einsatzmittel auf Fehler überprüft.
    Als Kriterien für die fehlerhaften Hilfsfristen gelten:
    - Hilfsfrist ist kleiner als 0 Minuten
    - Hilfsfrist ist größer als 60 Minuten

    Parameter:
    df (dataframe): Dataframe auf dem die Operationen ausgeführt werden sollen
    '''

    # Dataframe nach Einsatznummer und Hilfsfrist (Zeit) sortieren
    df.sort_values(by=[col_einsatz_nr, col_zeit_hilfsfrist_em], inplace=True)

    # Speicherung aller fehlerhaften Einsätze zu späteren Ausgabe an Benutzer
    err = 0 

    # Hilfsfrist für jeden Einsatz berechnen
    df[col_zeit_hilfsfrist] = np.nan
    current_einsatz = None
    for index, row in df.iterrows():
        if current_einsatz != row[col_einsatz_nr]:
            current_einsatz = row[col_einsatz_nr]
            if row[col_zeit_hilfsfrist_em] <= 0.0 or row[col_zeit_hilfsfrist_em] >= 60.0:
                 err += 1
            else:
                df.at[index, col_zeit_hilfsfrist] = row[col_zeit_hilfsfrist_em]
    print(str(err) + ' Einsätze wiesen fehlerhafte Werte auf und wurden bei der Hilfsfristberechnung übersprungen.')
    
    # Filtern von Einsätzen mit negativen Werten oder einer Hilfsfrist von über 60 Minuten (für Einsatzmittel)
    for index, row in df.iterrows():
        if row[col_zeit_hilfsfrist_em] <= 0.0 or row[col_zeit_hilfsfrist_em] >= 60.0:
            row[col_zeit_hilfsfrist_em] = np.nan

    return df


def main():
    '''main function'''

    # Daten Importieren
    data = import_data()

    # Nan Werte definieren
    data = data.replace(nan_value, np.nan)
    print('NaN Werte wurden definiert. \n')

    # Filtern von Spalten
    print('******************** Filterung ********************')
    print('Nicht benötigte Spalten werden entfernt...')
    # Dataframe verkleinern 
    data = data[[
        col_id,
        col_einsatz_nr,
        col_auftrag_nr,
        col_em,
        col_em_typ,
        col_stichwort,
        col_fehleinsatz,
        col_einsatz_ort,
        col_einsatz_objekt_name,
        col_einsatz_objekt_typ,
        col_einsatz_lat,
        col_einsatz_lon,
        col_s3_lat,
        col_s3_lon,
        col_ziel_ort,
        col_ziel_objekt_name,
        col_ziel_objekt_typ,
        col_status_alarm,
        col_ts_beginn_hilfsfrist,
        col_ts_alarm,
        col_ts_s3,
        col_ts_s4,
        col_ts_s7,
        col_ts_s8,
        col_ts_s1,
        col_ts_s2,
    ]].copy()
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    # Stichwörter Bezeichnungen und Grundstichwörter definieren
    print('Stichwörter werden gefiltert...')
    data = define_Stichwort(data, file_matching_stichwort)
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    # Einsatzmitteltypen filtern
    print('Einsatzmitteltypen werden gefiltert...')
    data = filter_value(data, file_em_typ, col_em_typ)
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    # Datenbereinigung
    print('******************** Datenbereinigung ********************')
    data = del_nanvalue(data, col_ts_alarm) # kein Alarm löschen
    data = del_nanvalue(data, col_ts_s3)    # Einsätze ohne Status 3 herausfiltern
    data = del_nanvalue(data, col_ts_s4)    # Einsätze ohne Status 4 herausfiltern
    data = del_koordinaten(data, col_einsatz_lat, col_einsatz_lon)  # Einsätze ohne Koordinaten herausfiltern
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    # Koordinaten umwandeln und korrigieren
    print('******************** Koordinaten verarbeiten ********************')
    # Koordinaten Einsatz verarbeiten
    print('Koordinaten für Einsatz werden verarbeitet...')
    data = correct_coord(data, col_einsatz_lat, col_einsatz_lon)
    data[col_einsatz_coord] = data.apply(create_col_coord, axis=1, args=(col_einsatz_lat, col_einsatz_lon))
    # Koordinaten S3 generieren
    print('Koordinaten für S3 werden verarbeitet...')
    data = correct_coord(data, col_s3_lat, col_s3_lon)
    data[col_s3_coord] = data.apply(create_col_coord, axis=1, args=(col_s3_lat, col_s3_lon))
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    print('******************** Berechnungen von Zeiten ********************')
    print('Wandle Zeitformat um...')
    data[col_datum] = pd.to_datetime(data[col_ts_alarm], format='%d.%m.%Y %H:%M:%S').dt.to_period('M')
    data[col_ts_alarm] = pd.to_datetime(data[col_ts_alarm], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_beginn_hilfsfrist] = pd.to_datetime(data[col_ts_beginn_hilfsfrist], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s3] = pd.to_datetime(data[col_ts_s3], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s4] = pd.to_datetime(data[col_ts_s4], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s7] = pd.to_datetime(data[col_ts_s7], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s8] = pd.to_datetime(data[col_ts_s8], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s1] = pd.to_datetime(data[col_ts_s1], format='%d.%m.%Y %H:%M:%S')
    data[col_ts_s2] = pd.to_datetime(data[col_ts_s2], format='%d.%m.%Y %H:%M:%S')

    print('Berechne Hilfsfrist...')
    data = time_difference(data, col_zeit_hilfsfrist_em, col_ts_beginn_hilfsfrist, col_ts_s4)
    data = calculate_hilfsfrist(data)
    #data = data.drop('temp', axis=1)
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    print('Berechne Ausrückzeiten...')
    data = time_difference(data, col_zeit_ausruecken, col_ts_alarm, col_ts_s3)
    print('Berechne Anfahrtszeiten...')
    data = time_difference(data, col_zeit_anfahrt, col_ts_s3, col_ts_s4)
    print('Berechne Versorgungszeiten...')
    data = time_difference(data, col_zeit_versorgung, col_ts_s4, col_ts_s7)
    print('Berechne Transportzeiten...')
    data = time_difference(data, col_zeit_transport, col_ts_s7, col_ts_s8)
    print('Berechne Zeiten S8...')
    data = time_difference(data, col_zeit_ziel, col_ts_s8, col_ts_s1)
    print('Berechne Einsatzdauer bis S8...')
    data = time_difference(data, col_zeit_gesamt_pat, col_ts_alarm, col_ts_s8)
    print('Berechne Einsatzdauer bis S1...')
    data = time_difference(data, col_zeit_gesamt, col_ts_alarm, col_ts_s1)
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    print('******************** Zusätzliche Spalten werden generiert ********************')
    ### Hilfsfrist TRUE/FALSE berechen
    print('Einhaltung der Hilfsfrist wird berechnet...')
    data[col_hilfsfrist] = np.where(((data[col_zeit_hilfsfrist] <= hilfsfrist)), True, False)

    ### Fehleinsatz TRUE/FALSE berechen/umcodieren
    print('Werte der Spalte Fehleinsatz werden umcodiert...')
    data[col_fehleinsatz] = np.where(((data[col_fehleinsatz] == 1.0)), True, False)
    
    ### Distancen berechnen
    print('Berechne Distanzen zur Einsatzstelle...')
    data[col_distance_einsatz] = data.apply(calculate_distance, axis=1, args=(col_s3_coord, col_einsatz_coord))
    data[col_distance_einsatz] = data[col_distance_einsatz].replace(0.0, np.nan)

    ### durchschnittliche Geschwindigkeit berechnen
    print('Berechne durchschnittliche Geschwindigkeiten...')
    data[col_geschwindigkeit_anfahrt] = data.apply(calculate_speed, axis=1, args=(col_distance_einsatz, col_zeit_anfahrt))
    data[col_geschwindigkeit_anfahrt] = data[col_geschwindigkeit_anfahrt].replace(0.0, np.nan)

    ### Spalte EM Wache generieren
    print('Spalte ' + col_em_wache + ' wird generiert...')
    data = neue_spalte(data, col_em, col_em_wache, '-')

    ### Spalte Wache generieren
    print('Spalte ' + col_wache + ' wird generiert...')
    data = neue_spalte(data, col_em, col_wache, '/')

    ### Spalte EM RDB generieren
    print('Spalte ' + col_em_rdb + ' wird generiert...')
    data = neue_spalte(data, col_em, col_em_rdb, ' ')

    ### Koordinaten für Wachen importieren
    print('Koordinaten für Wachen werden in Datensatz geschrieben...')
    data = define_Wache_coord(data, file_wachen_coord)

    ### Umwandlung in geodataframe
    data = gpd.GeoDataFrame(data,
            geometry = gpd.points_from_xy(data[col_einsatz_lon], data[col_einsatz_lat]), 
            crs = 'EPSG:4326')

    # Zusätzliche Informationen zum Datensatz hinzufügen (räumlich)
    print('Zusätzliche räumliche Daten werden verknüpft...')
    data = spatial_join(data)
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    # bestimmte RDB Herkunft des EM filtern
    try:
        print('EM werden nach RDB gefiltert...')
        data = define_em_rdb(data, '../config/preprocessing/filter_em_rdb.csv')
        print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')
    except:
        print('Es wurde keine Datei für die Filterung von Rettungsdienstbereichen gefunden.\n')

    # Zeilen löschen die keine Eintrag in der Spalte RDB haben
    print('Zeilen ohne RDB werden gelöscht...')
    data = data[data[col_rdb].notna()]
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

    ### Statistiken speichern
    # Stichwörter
    col_list = [col_stichwort, col_stichwort_bez, col_grundstichwort]
    save_stats(data, col_list, col_stichwort)

    # Rettungsdienstbereiche der EM
    col_list = [col_em_rdb]
    save_stats(data, col_list, col_em_rdb)
    
    print('')

    # Daten speichern
    print('Daten werden gespeichert...')
    data.to_csv('../data/data.csv', sep=';')
    data.to_pickle('../data/data.pkl')
    print('Erledigt. Größe Datensatz: ' + str(data.shape) + '\n')

if __name__ == '__main__':
    main()