# -*- coding: utf-8 -*-

# import modules
import os
import sys
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from ohsome import OhsomeClient
from sklearn.cluster import DBSCAN

# Working directory setzen
sys.path.append(str(Path(__file__).parent.parent.resolve()))
path = os.getcwd()
print('Working directory: %s\n' %path)

# config importieren
from config.config import *

# activate seaborn
sns.set()

# Warnungen deaktivieren
pd.options.mode.chained_assignment = None  # default='warn'

input_data = '../data/data.pkl'

def import_data():
    '''Daten importieren und in GeoDataFrame umwandeln.'''

    print('******************** Datenimport ********************')
    print('Importiere Datensatz. Dies kann eine Weile Minuten dauern...')
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
    
    # Datensatz in UTM 32N umwandeln
    gdf = gdf.to_crs('EPSG:25832')
    print('Datenimport erfolgreich.\n')
    print('Größe Datensatz: ' + str(df.shape))
    print('')

    return gdf

def import_rdb():
    '''Rettungsdienstbereiche importieren und in GeoDataFrame umwandeln.'''

    # Import Rettungsdienstbereich
    try:
        rdb = gpd.read_file('../data/rdb.gpkg')
        rdb = rdb.loc[(rdb['RDB'] == rdb_name)]
        rdb = rdb.to_crs(epsg=4326)
    except FileNotFoundError:
        print('Datei ../data/rdb.gpkg konnte nicht gefunden werden.')
        sys.exit(1)
    return rdb

def filter_data(gdf):
    '''Daten filtern nach RDB, Grundstichwörtern und Stichwörtern.'''

    # nach eigenem Rettungsdienstbereich filtern
    gdf = gdf.loc[(gdf[col_rdb] == rdb_name)]

    # nur für Hilfsfrist relevante Grundstichwörter filtern (definiert in config.py)
    gdf = gdf.loc[gdf[col_grundstichwort].isin(gs_nr)]

    # Bestimmte Stichwörter nicht verwenden (siehe config.py)
    for stichwort in sw_nicht_verwenden:
        gdf = gdf.loc[gdf[col_stichwort] != stichwort]

    return gdf

def download_osm_data(filter):
    '''OSM Daten herunterladen und als gpkg speichern.'''

    client = OhsomeClient()

    file = '../data/osm/' + filter + '.gpkg'

    # Polygon Rettungsdienstbereich importieren
    rdb = import_rdb()
    
    print(filter + ' wird heruntergeladen...')

    response = client.elements.geometry.post(bpolys=rdb, filter='landuse=' + filter)
    response_gdf = response.as_dataframe()
    response_gdf.to_file(file)
    print(file + ' erfolgreich gespeichert.')

def import_osm_data():
    '''OSM Daten über die ohsome API herunterladen und in GeoDataFrame zusammenführen.
    Falls die Daten bereits vorhanden sind, werden diese importiert.'''
  
    print('******************** OSM Daten Import ********************')

    # Als Ausgangsdatendatz wird 'residential' verwendet.
    filter = 'residential'
    file = '../data/osm/' + filter + '.gpkg'
    try:
        osm = gpd.read_file(file)
        print(file + ' gefunden.')
    except Exception as Err:
        download_osm_data(filter)
        osm = gpd.read_file(file)
    osm = osm.drop('@snapshotTimestamp', axis=1)

    # Alle landuse Flächen imporiteren, bzw. herunterladen. Liste ist in config.py definiert.
    for filter in osm_filter:
        # OSM Daten importieren. Falls nicht vorhanden, wird der Datensatz heruntergeladen.
        file = '../data/osm/' + filter + '.gpkg'
        try:
            osm_ = gpd.read_file(file)
            print(file + ' gefunden.')
        except Exception as Err:
            download_osm_data(filter)
            osm_ = gpd.read_file(file)
        osm_ = osm_.drop('@snapshotTimestamp', axis=1)
        
        # Daten zusammenführen
        osm = osm.merge(osm_, how='outer', on='@osmId')
        # Geometry Spalten zusammenführen
        osm['geometry'] = osm['geometry_x'].combine(osm['geometry_y'], lambda x1, x2: x1 if x1 else x2)
        # 'Alte' Spalten entfernen
        osm = osm.drop('geometry_x', axis=1)
        osm = osm.drop('geometry_y', axis=1)
    
    osm = gpd.GeoDataFrame(osm, geometry='geometry')
    osm = osm.dissolve().explode(index_parts=True)
    osm = osm.reset_index(drop=True)
    osm.crs = 'EPSG:4326'
    osm = osm.to_crs('EPSG:25832')
    print('')

    return osm

def create_cluster(gdf):
    '''Cluster mit DBSCAN erstellen.'''

    gdf_coord = gdf.to_crs('EPSG:4326')
    gdf_coord['lat'] = gdf['geometry'].y
    gdf_coord['lon'] = gdf['geometry'].x

    data = gdf_coord[['lat', 'lon']].to_numpy()

    # Clustering
    db = DBSCAN(eps=200, min_samples=30).fit(data)
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    print('Geschätzte Anzahl Cluster: %d' % n_clusters_)
    print('Geschätzte Anzahl noise points: %d' % n_noise_)

    gdf['cluster_id'] = labels

    return gdf

def detect_outlier(polygons, points):
    '''Outlier im Datensatz identifizieren und diese in Datei speichern.'''

    print('Outlier werden identifiziert....')
    outlier = points.sjoin(polygons, how='left')
    outlier = outlier.loc[outlier['index_right'].isna()]
    outlier = outlier[[col_einsatz_nr, col_einsatz_coord, col_ts_alarm, col_stichwort, col_grundstichwort, 'geometry']]
    
    count_outlier = outlier[col_einsatz_nr].count()
    print('Identifizierte Outlier: ' + str(count_outlier))

    outlier.to_file('../data/osm/outlier.gpkg')

    return outlier

def create_convex_hull(gdf):
    '''Konvexe Hülle um Cluster erstellen.'''

    # Konvexe Hülle erstellen (basierend auf cluster_id)
    gdf = gdf.loc[gdf['cluster_id'] != -1]

    convex_hull = gdf.dissolve('cluster_id').convex_hull.reset_index()
    convex_hull = convex_hull.rename(columns={0: 'geometry'})
    convex_hull = gpd.GeoDataFrame(convex_hull, geometry='geometry')
    convex_hull = convex_hull[convex_hull.geom_type=='Polygon']

    convex_hull.to_file('../data/osm/outlier_convex_hull.gpkg')

    return convex_hull


def main():
    '''main function'''
       
    # Import Data (Datensatz mit Einsätzen)
    data_einsatz = import_data()

    # Einsatzdaten filtern
    data_einsatz = filter_data(data_einsatz)    

    # OSM Daten importieren
    data_osm = import_osm_data()

    print('******************** Generierung Cluster ********************')
    # Outlier Detection
    data_einsatz_ = detect_outlier(data_osm, data_einsatz)

    # Outlier mit DBSCAN clustern
    cluster = create_cluster(data_einsatz_)

    # Konvexe Hülle um Cluster erstellen
    outlier_convex_hull = create_convex_hull(cluster)

    # Regionen auf Grundlage der OSM Daten und Konvexen Hüllen erstellen
    regions = pd.concat([data_osm, outlier_convex_hull], ignore_index=True)
    regions = regions.dissolve().explode(index_parts=True)
    regions = regions.reset_index(drop=True)
    regions = regions.to_crs('EPSG:25832')
    print('Cluster wurden zu Regionen hinzugefügt.')

    # Grenzen importieren
    gdf = gpd.read_file('../data/grenzen.gpkg')
    gdf = gdf.to_crs('EPSG:25832')
    # regionen an den Grenzen schneiden
    regions = gpd.overlay(regions, gdf, how='intersection')
    print('Regionen wurden verschnitten.')
    
    # überflüssige Spalten löschen
    regions = regions.drop('@osmId', axis=1)
    regions = regions.drop('id', axis=1)
    regions = regions.drop('admin_level', axis=1)
    regions = regions.drop('cluster_id', axis=1)
    regions['area_id'] = regions.index
    print('Nicht benötigte Spalten wurden entfernt...')

    # Kleinere Regionen aus Datenschutzgründen entfernen (definiert in config.py)
    regions_size = regions.area
    regions = regions[regions_size >= region_min]
    print('Regionen kleiner als ' + str(region_min) + ' m² wurden entfernt...')

    # Regionen in Datei speichern
    regions.to_file('../data/region/regions.gpkg')
    print('Regionen wurden in ../data/region/regions.gpkg gespeichert.')
    print('')

    # Check outliers
    print('******************** Berechnung Statistiken ********************')
    data_einsatz_ = detect_outlier(regions, data_einsatz)
    count_gesamt = data_einsatz[col_einsatz_nr].count()
    count_outlier = data_einsatz_[col_einsatz_nr].count()
    percent = np.round((count_outlier / count_gesamt) * 100, 2)

    print('Anteil Outlier: ' + str(percent) + ' %')

if __name__ == '__main__':
    main()