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

def import_data():
    '''Datenimport'''

    print('******************** Datenimport ********************')
    print("Importiere Datensatz. Dies kann eine Weile Minuten dauern...")
    df = pd.read_pickle('../data/data.pkl')
    # GeoDataFrame erzeugen
    gdf = gpd.GeoDataFrame(df,
        geometry = gpd.points_from_xy(df[col_einsatz_lon], df[col_einsatz_lat]), 
        crs = 'EPSG:4326')
    print('Datenimport erfolgreich.')
    print('Größe Datensatz: ' + str(df.shape) + '\n')
    return gdf

def get_years(df):
    '''Alle im Datensatz enthaltenen Jahre in Liste speichern und zurückgeben'''

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

def stats_summe_zeit(df, column, parameter_list, zeit, title=''):
    '''Erstellung eines Plots für gesamten Zeitraum oder für einzelne Jahre, Monate, Tage oder Stunden.
    Auf Grundlage der Spalte Einsatznummer werden die Daten summiert und in einem Plot dargestellt.
    
    Paramter:
    df (dataframe): Datensatz
    column (string): Name der Spalte die ausgewertet werden soll
    parameter_list (list): Liste der Parameter die in der Spalte enthalten sind
    zeit (string): Auswahlkriterium in Funktion / Definition Zeitraum
    title (string): Titel (Wenn leer wird Spaltenname verwendet)
    '''

    if title == '':
        title = column
    
    if zeit == 'all':
        # Plot für gesamten Zeitraum erstellen
        col_date = 'Datum'
        df[col_date] = df[col_ts_alarm].dt.to_period('M')

        for parameter in parameter_list:
            df_stats = df.loc[(df[column] == parameter)]
            df_stats.groupby(col_date)[col_einsatz_nr].nunique().plot(label=parameter)
    
    # Plot für einzelne Jahre erstellen
    elif zeit == 'J':
        col_date = 'Jahr'
        df[col_date] = df[col_ts_alarm].dt.to_period('M')

        for parameter in parameter_list:
            df_stats = df.loc[(df[column] == parameter)]
            df_stats.groupby(df[col_ts_alarm].dt.year)[col_einsatz_nr].nunique().plot(label=parameter)
    
    # Plot für einzelne Monate erstellen
    elif zeit == 'M':
        col_date = 'Monat'
        df[col_date] = df[col_ts_alarm].dt.to_period('M')

        for parameter in parameter_list:
            df_stats = df.loc[(df[column] == parameter)]
            df_stats.groupby(df[col_ts_alarm].dt.month)[col_einsatz_nr].nunique().plot(label=parameter)
    
    # Plot für einzelne Tage erstellen
    elif zeit == 'D':
        col_date = 'Tag'
        df[col_date] = df[col_ts_alarm].dt.to_period('M')

        for parameter in parameter_list:
            df_stats = df.loc[(df[column] == parameter)]
            df_stats.groupby(df[col_ts_alarm].dt.day)[col_einsatz_nr].nunique().plot(label=parameter)
    
    # Plot für einzelne Stunden erstellen
    elif zeit == 'H':
        col_date = 'Uhrzeit'
        df[col_date] = df[col_ts_alarm].dt.to_period('M')

        for parameter in parameter_list:
            df_stats = df.loc[(df[column] == parameter)]
            df_stats.groupby(df[col_ts_alarm].dt.hour)[col_einsatz_nr].nunique().plot(label=parameter)

    # Plotten
    plt.legend()                    # Legende anzeigen
    plt.title(title)                # Titel hinzufügen
    plt.xlabel(col_date)            # Beschriftung x-Achse
    plt.ylim(bottom=0)              # y-Achse bei 0 starten
    plt.ylabel('Anzahl Einsätze')   # Beschriftung y-Achse
    plt.tight_layout()              # Tight layout verwenden
    plt.show()                      # Plot anzeigen

def create_list(df, column):
    '''Liste mit allen Einträgen in einer Spalte erstellen und zurückgeben'''

    list = df[column].unique()
    list = list.tolist()
    return list
    
def stats_gesamt(df, column, list=''):

    # Nach Jahren gruppieren und Spalte Jahr zu Datensatz hinzufügen
    col_date = 'Jahr'
    df[col_date] = df[col_ts_alarm].dt.to_period('M')
    df[col_date] = df[col_date].dt.year

    # Liste erstellen
    if list == '':
        list = create_list(df, column)

    # "Leeren" Dataframe erstellen, in diesen werden die Statistiken geschrieben
    df_gesamt = df.groupby(col_date)[column].agg(['count'])
    df_gesamt = df_gesamt.drop('count', axis=1)

    # für jeden Eintrag in der Liste Statistiken für jedes Jahr generieren und an den vorher erstellten df anfügen
    for entry in list:
        df_ = df.loc[(df[column] == entry)]
        df_ = df_.groupby(col_date)[col_einsatz_nr].agg(['nunique'])
        df_ = df_.rename(columns={'nunique': entry})
        df_gesamt = df_gesamt.merge(df_, how='left', on='Jahr')

        # falls Einsatzzahlen in manchen Jahren > 0 waren wird dies gefiltert
        if df_gesamt.isnull().values.sum() > 0:
            df_gesamt = df_gesamt.dropna(axis=1)
            print(str(entry) + ' hat zu wenig Daten und wurde gelöscht')
            print(df_)
            print('')
    
    # Ergebnisse als csv Datei speichern
    print(df_gesamt)
    
    # Ergebnis plotten
    fig, ax = plt.subplots(layout='constrained', figsize=(30, 15))
    df_gesamt.plot(kind='bar', label=entry, ax=ax)
    for container in ax.containers:
        ax.bar_label(container)
    locs, labels = plt.xticks()
    
    plt.xlabel('Jahr')                                      # Beschriftung x-Achse
    plt.setp(labels, rotation=45)                           # x-Achse drehen
    plt.ylabel('Anzahl Einsätze')                           # Beschriftung y-Achse
    plt.title(column)                                       # Titel hinzufügen
    plt.tight_layout()                                      # Tight layout verwenden
    plt.show()
    print('Statistiken für ' + column + ' wurden erstellt')


def stats_stichwort_woche_multiple(df, column, parameter_list):
    '''Berechnet die zeitliche Verteilung der Einsatzhäufigkeit eines Stichwortes über eine gesamte Woche'''
    
    col_date = 'Uhrzeit'
    col_wochentag = 'wochentag'
    week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    df[col_wochentag] = df[col_ts_alarm].dt.day_name()

    combined_data = []  # Liste für kombinierte Daten aller Parameter

    for parameter in parameter_list:
        df_ = df.loc[(df[column] == parameter)]
        df_ = df_.groupby([df_[col_ts_alarm].dt.hour, df_[col_wochentag]])[col_einsatz_nr].nunique().reset_index().dropna()
        df_['Parameter'] = parameter  # Füge eine Spalte für den Parameter hinzu
        combined_data.append(df_)

    combined_df = pd.concat(combined_data, ignore_index=True)  # Kombiniere

    # Plotten
    sns.set_style("white")
    ax = sns.FacetGrid(combined_df, col=col_wochentag, hue='Parameter', col_wrap=7, height=6, col_order=week)
    ax.map(sns.lineplot, col_ts_alarm, col_einsatz_nr)

    plt.tight_layout()
    plt.legend()
    plt.show()

def clear_screen():
    '''Konsole leeren (abhängig vom Betriebssystem)'''

    if os.name == 'posix':      # für Linux/Unix
        _ = os.system('clear')
    else:                       # für Windows
        _ = os.system('cls')

def change_list_gs():
    '''globale Liste mit Grundstichwörtern ändern'''

    global list_gs_
    global list_gs
    list_gs = []
    while True:
            print('Geben Sie im nachfolgenden die Grundstichwörter ein, die sie zur Liste hinzufügen möchten.')
            print('> Drücken Sie die Eingabetaste um Ihre Eingabe der Liste hinzuzufügen.')
            print('> Drücken Sie die Eingabetaste ohne vorherige Eingabe zum beenden.')
            print('> Geben Sie -1 ein um die originale Liste wiederherzustellen.')
            print('')
            print('Original: ' + str(list_gs_))
            print('Neu: ' + str(list_gs) + '\n')
            i = input('>> ')
            if (i == ''):
                break
            if (i == '-1'):
                list_gs = list_gs_
                break
            else:
                list_gs.append(i)
                clear_screen()

def change_list_em_typ():
    '''globale Liste mit Einsatzmitteltypen ändern'''

    global list_em_typ  # Globale Variable deklarieren
    list_em_typ = []
    while True:
            print('Geben Sie im nachfolgenden die Einsatzmitteltypen ein, die sie zur Liste hinzufügen möchten.')
            print('> Drücken Sie die Eingabetaste um Ihre Eingabe der Liste hinzuzufügen.')
            print('> Drücken Sie die Eingabetaste ohne vorherige Eingabe zum beenden.')
            print('> Geben Sie -1 ein um die originale Liste wiederherzustellen.')
            print('')
            print('Original: ' + str(list_em_typ_))
            print('Neu: ' + str(list_em_typ) + '\n')
            i = input('>> ')
            if (i == ''):
                break
            if (i == '-1'):
                list_em_typ = list_em_typ_
                break
            else:
                list_em_typ.append(i)
                clear_screen()

def change_list_sw():
    '''globale Liste mit Stichwörtern ändern'''

    global list_sw  # Globale Variable deklarieren
    list_sw = []
    while True:
            print('Geben Sie im nachfolgenden die Stichwörter ein, die sie zur Liste hinzufügen möchten.')
            print('> Drücken Sie die Eingabetaste um Ihre Eingabe der Liste hinzuzufügen.')
            print('> Drücken Sie die Eingabetaste ohne vorherige Eingabe zum beenden.')
            print('> Geben Sie -1 ein um die originale Liste wiederherzustellen.')
            print('')
            print('Original: ' + str(list_sw_))
            print('Neu: ' + str(list_sw) + '\n')
            i = input('>> ')
            if (i == ''):
                break
            if (i == '-1'):
                list_sw = list_sw_
                break
            else:
                list_sw.append(i)
                clear_screen()

def print_menu():
    '''Hauptmenü'''

    clear_screen()  # Konsole leeren

    print('Grunstichwörter: ' + str(list_gs))
    print('Einsatzmitteltypen: ' + str(list_em_typ))
    print('Stichwörter: ' + str(list_sw))
    print('Jahre: ' + str(list_years))
    print('')
    print('A - Grundstichwörter auswählen')
    print('B - Einsatzmitteltypen auswählen')
    print('C - Stichwörter auswählen (nur bei bestimmten Auswertungen erforderlich)')
    print('')
    print('1 - Auswertung Grundstichwörter')
    print('2 - Auswertung Einsatzmittel')
    print('3 - Auswertung Einsätze nach Rettungsdienstbereichen')
    print('4 - Auswertung Einsatzmittel nach Rettungsdienstbereichen')
    print('5 - Auswertung Fehleinsätze')
    print('')
    print('11 - Zeitliche Auswertung Grundstichwörter')
    print('12 - Zeitliche Auswertung Einsatzmitteltypen')
    print('13 - Zeitliche Auswertung Fehleinsätze')
    print('14 - Zeitliche Auswertung Stichwörter')
    print('')
    print('21 - Zeitliche Auswertung über Woche (Grundstichwörter)')
    print('22 - Zeitliche Auswertung über Woche (Einsatzmitteltypen)')
    print('23 - Zeitliche Auswertung über Woche (Stichwörter)')
    print('')
    print('99 - Beenden')

def menu_stats_summe_zeit():
    '''Untermenü für zeitliche Auswertungen'''

    clear_screen()  # Konsole leeren
    ### Zeitliche Auswertung Grundstichwörter (Summe)
    print('Geben Sie eine beliebige Eingabe ein um eine Auswertung für den gesamten Zeitraum zu erstellen.')
    print('Alternativ könne Sie aus folgenden Optionen wählen:')
    print('J - Summe pro Jahr')
    print('M - Summe pro Monat')
    print('D - Summe pro Tag im Monat')
    print('H - Summe nach Uhrzeit')

    eingabe = input('>> ').upper()

    if eingabe != 'J' and eingabe != 'M' and eingabe != 'D' and eingabe != 'H':
        eingabe = 'all'

    return eingabe

def main():
    '''main function'''
    
    # Daten importieren
    data = import_data()

    # Liste mit allen Jahren erstellen
    global list_years                   # globale Variable deklarieren
    global list_years_                  # globale Variable deklarieren
    list_years = get_years(data)        #
    list_years_ = list_years.copy()     # Kopie der globalen Variable erstellen (um Origional zu behalten)


    # Liste mit allen Einsatzmitteltypen erstellen
    global list_em_typ                  # globale Variable deklarieren
    global list_em_typ_                 # globale Variable deklarieren
    list_em_typ = get_em_typ(data)      # 
    list_em_typ_ = list_em_typ.copy()   # Kopie der globalen Variable erstellen (um Origional zu behalten)

    # Liste Grundstichwörter
    list_gs_ = list_gs.copy()           # Kopie der globalen Variable erstellen (um Origional zu behalten)
    
    # Liste Stichwörter
    global list_sw                      # globale Variable deklarieren
    global list_sw_                     # globale Variable deklarieren
    list_sw = []                        # Liste initialisieren
    list_sw_ = list_sw.copy()           # Kopie der globalen Variable erstellen (um Origional zu behalten)

    # Liste bool für Fehleinsätze
    global list_bool                    # globale Variable deklarieren
    list_bool = [True, False]           # Liste initialisieren

    # 
    while True:
        print_menu()        # Menü anzeigen
        x = input('>> ')    # Eingabe Konsole
        clear_screen()      # Konsole leeren

        # Paramter ändern
        if x.upper() == 'A':
            change_list_gs()
        elif x.upper() == 'B':
            change_list_em_typ()
        elif x.upper() == 'C':
            change_list_sw()

        # Auswertungen
        elif x == '1':
            ### Auswertung Grundstichwörter
            stats_gesamt(data, col_grundstichwort, list_gs)
            input('\nDrücken Sie eine beliebige Taste zum fortfahren...')
        elif x == '2':
            ### Auswertung Einsatzmittel
            stats_gesamt(data, col_em_typ)
            input('\nDrücken Sie eine beliebige Taste zum fortfahren...')
        elif x == '3':
            ### Auswertung Einsätze in Rettungsdienstbereichen
            stats_gesamt(data, col_rdb)
            input('\nDrücken Sie eine beliebige Taste zum fortfahren...')
        elif x == '4':
            ### Auswertung Einsatzmittel aus Rettungsdienstbereichen
            stats_gesamt(data, col_em_rdb)
            input('\nDrücken Sie eine beliebige Taste zum fortfahren...')
        elif x == '5':
            ### Auswertung Fehleinsätze
            #print('Geben Sie das Grundstichwort ein, für das Sie eine Auswertung erstellen möchten.')
            #gs = input('>> ').upper()
            #data_gs = data.loc[(data[col_grundstichwort] == gs)]
            stats_gesamt(data, col_fehleinsatz, list_bool)
            input('\nDrücken Sie eine beliebige Taste zum fortfahren...')

        # Zeitliche Auswertungen
        elif x == '11':
            print('Zeitliche Auswertung Grundstichwörter (Summe)')
            parameter = menu_stats_summe_zeit()
            stats_summe_zeit(data, col_grundstichwort, list_gs, parameter)
        elif x == '12':
            print('Zeiliche Auswertung Einsatzmitteltypen (Summe)')
            parameter = menu_stats_summe_zeit()
            stats_summe_zeit(data, col_em_typ, list_em_typ, parameter)
        elif x == '13':
            print('Geben Sie das Grundstichwort ein, für das Sie eine Auswertung erstellen möchten:')
            gs = input('>> ').upper()
            data_gs = data.loc[(data[col_grundstichwort] == gs)]

            print('Zeitliche Auswertung Fehleinsätze (Summe)')
            parameter = menu_stats_summe_zeit()
            stats_summe_zeit(data_gs, col_fehleinsatz, list_bool, parameter)
        elif x == '14':
            print('Zeitliche Auswertung Stichwörter (Summe)')
            parameter = menu_stats_summe_zeit()
            stats_summe_zeit(data, col_stichwort, list_sw, parameter)

        # Zeitliche Auswertungen über Woche
        elif x == '21':
            # Zeitlicher Verlauf über Woche (Grundstichwort)
            print('Grundstichwörter über gesamte Woche')
            stats_stichwort_woche_multiple(data, col_grundstichwort, list_gs)
        elif x == '22':
            # Zeitlicher Verlauf über Woche (Einsatzmitteltypen)
            print('Einsatzmitteltypen über gesamte Woche')
            stats_stichwort_woche_multiple(data, col_grundstichwort, list_em_typ)
        elif x == '23':
            # Zeitlicher Verlauf über Woche (Stichwörter)
            print('Stichwörter über gesamte Woche')
            stats_stichwort_woche_multiple(data, col_stichwort, list_sw)
        elif x == '99':
            break
    
    

if __name__ == '__main__':
    main()