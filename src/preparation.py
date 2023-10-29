# -*- coding: utf-8 -*-

# import modules
import sys
import os
import pandas as pd
from urllib.request import urlretrieve
from pathlib import Path

# Working directory setzen
sys.path.append(str(Path(__file__).parent.parent.resolve()))
path = os.getcwd()
print("Working directory: %s\n" %path)

# Warnungen pandas ausschalten
pd.options.mode.chained_assignment = None  # default='warn'

if len(sys.argv) == 2:
    input_data = sys.argv[1]
else:
    input_data = input("Geben Sie den Pfad für Ihren Datensatz an: ")

def get_group_col(df, column, file_name):
    '''Gruppiert die Einträge nach einer übergebenen Liste an Spaltennamen und speichert diese in Datei ab.'''

    df = df.groupby(column)[column].count()
    # Ergebnisse in Datei speichern
    output_file = '../config/preparation/output_'+ str(file_name) +'.csv'
    df.to_csv(output_file, sep=';')
    print(column + ' in Datei ' + output_file + ' gespeichert')

def create_folders():
    '''Erstellt die benötigten Unterordner.'''

    # Unterordner erstellen
    print('Unterordner werden erstellt...')
    folder_list = [
        '../config/preparation/',
        '../config/preprocessing/',
        '../output/',
        '../output/RDB/',
        '../output/Kommunen/',
        '../output/Fahrzeit/',
        '../output/Versorgungszeit/',
        '../data/',
        '../data/osm/',
        '../data/LAU/',
        '../data/region/'
    ]
    for folder in folder_list:
        try:
            os.mkdir(folder)
            print('Verzeichnis ' + folder + ' wurde angelegt.')
        except Exception as Err:
            print(Err)

def download_data():
    '''Lokale Administrative Einheiten von EUROSTAT herunterladen.'''

    # Über die Variable lau_year ist es möglich einen neueren (oder älteren) Datensatz für die Bevölkerungsdaten herunterzuladen.
    # Bitte beachten Sie, dass durch Eurostat nicht für alle Jahre Daten zur Verfügung gestellt werden.
    # Insbesondere neuere Datensätze sind teilweise erst verzögert verfügbar.
    lau_year = 2020
    lau_url = ('https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_' + str(lau_year) + '_4326.geojson')
    lau_file = '../data/LAU/LAU_RG_01M_' + str(lau_year) + '_4326.geojson'

    print('Lokale Administrative Einheiten für das Jahr ' + str(lau_year) + ' werden von EUROSTAT heruntergeladen...')
    filename = lau_file
    urlretrieve(lau_url, lau_file)
    print('Datensatz erfolgreich heruntergeladen.')

def main():
    '''main function'''

    # Daten importieren
    try:
        print("Importiere Datensatz. Dies kann eine Weile dauern...")
        data = pd.read_csv(input_data, sep = ';')
    except FileNotFoundError:
        print(f"Error: Die Datei {input_data} konnte nicht importiert werden.")
        sys.exit(1)
    print('Datenimport erfolgreich.')
    print('Größe Datensatz: ' + str(data.shape))
    print('')
    
    # Unterordner erstellen
    create_folders()

    # LAU Daten herunterladen
    download_data()

    print('\nBitte geben Sie im nachfolgenden die Namen der entsprechenden Spalten aus Ihrem Datensatz an:')
    
    ## Dokument mit allen Stichwörtern generieren
    col_stichwort = input('Stichwort: ')
    get_group_col(data, col_stichwort, 'stichwort')

    ## Dokument mit allen Einsatzmitteltypen generieren
    col_em_typ = input('Einsatzmitteltyp: ')
    get_group_col(data, col_em_typ, 'em_typ')

    ## Dokument mit allen Spalten generieren
    file_columns = '../config/preparation/output_spalten.csv'
    file = open(file_columns, 'w')
    for col in data.columns[1:]:
        file.write(col + '\n')
    file.close()
    print('Dokument mit allen Spalten aus Datensatz in ' + file_columns + ' gepeichert.\n')

if __name__ == '__main__':
  main()