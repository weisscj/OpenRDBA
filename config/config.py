'''
Dieses Skript enthält die Konfiguration für das gesamte Tool. Vor der ersten Ausführung mit Ihren Daten müssen Sie sicherstellen,
dass Sie die Variblennamen korrekt an Ihren Datensatz anpassen. Des Weiteren können Sie hier die Paramter für Berechnungen definieren.
Gehen Sie dieses Dokument Zeile für Zeile durch und passen Sie die Parameter an Ihren Datensatz an. Sollten Sie Fragen haben,
schauen Sie bitte in die Dokumentation. Sollten weiterhin Unklarheiten bestehen oder es bei der Ausführung zu Problemen kommen,
erstellen Sie bitte ein Issue im zugehörigen GitHub Repository.
'''

#################### Paramter ####################

# Name des (eigenen) Rettungsdienstbereiches
rdb_name = ''

# Hilfsfrist (in Minuten)
hilfsfrist = 15

# Perzentil für die Hilfsfrist
hilfsfrist_perzentil = 95

# Spalte die den Beginn der Hilfsfrist definiert
col_ts_beginn_hilfsfrist = 'Beginn_Hilfsfrist'

# NaN / nodata Wert
nan_value = '-'

#################### Spaltennamen im Datensatz ####################
# Die nachfolgenden Variablen müssen mit den Spaltennamen in Ihrem Datensatz übereinstimmen!

# Spaltennamen
col_id = 'id'                   # ID
col_datum = 'Datum'             # Datum des Einsatzes
col_einsatz_nr = 'EinsatzNr'    # Einsatznummer
col_auftrag_nr = 'AuftragsNr'   # Auftragsnummer

col_em = 'EM'                   # Einsatzmittel / Funkrufnamen des Einsatzmittels
col_em_typ = 'EM_Typ'           # Einsatzmitteltyp

col_stichwort = 'Stichwort'             # Stichwort

col_fehleinsatz = 'Fehleinsatz'         # Fehleinsatz

# Einsatzstelle
col_einsatz_ort = 'E_Ort'               # Ort
col_einsatz_objekt_name = 'E_Name'      # Objekt Name
col_einsatz_objekt_typ = 'E_Typ'        # Objekt Typ
col_einsatz_lat = 'E_lat'               # Latitude (WGS84)
col_einsatz_lon = 'E_lon'               # Longitude (WGS84)

# Status 3
col_s3_lat = 'S3_lat'   # Latitude (WGS84)
col_s3_lon = 'S3_lon'   # Longitude (WGS84)

# Transportziel
col_ziel_lat = 'Z_lat'
col_ziel_lon = 'Z_lon'
col_ziel_ort = 'Z_Ort'
col_ziel_objekt_name = 'Z_Name'
col_ziel_objekt_typ = 'Z_Typ'

# Status bei Alarm
col_status_alarm = 'Status_Alarm'

# Zeitstempel (Beginn Hilfsfrist siehe oben)
col_ts_alarm = 'Alarm'  # Zeitstempel Alarm
col_ts_s3 = 'S3'    # Zeitstempel Status 3
col_ts_s4 = 'S4'    # Zeitstempel Status 4
col_ts_s7 = 'S7'    # Zeitstempel Status 7
col_ts_s8 = 'S8'    # Zeitstempel Status 8
col_ts_s1 = 'S1'    # Zeitstempel Status 1
col_ts_s2 = 'S2'    # Zeitstempel Status 2

#################### Paramter für Clustering (create_regions.py) ####################

# Bitte geben Sie im nachfolgenden alle Stichwörter an, welche Sie für das Clustering NICHT verwenden möchten.
# Empfohlen wird die Nichtverwendung von Verkehrsunfällen, da diese zu Artefakten in der räumlichen Darstellung führen können.
sw_nicht_verwenden = [
        'Stichwort 1',
        'Stichwort 2',
        'Stichwort 3'
    ]

# Mindestgröße der Region in m²
region_min = 50000 

# in dieser Liste sind die Filter für die OSM landuse Flächen definiert. Zusätzlich wird im Skript der Typ 'residential' verwendet.
# Verändern Sie diese Parmater nur dann, wenn Sie ganz genau wissen was Sie tun möchten!
osm_filter = ['commercial', 'industrial', 'retail', 'farmyard']

#################### Paramter für die Berechnung der Statistiken ####################
# >> Dieser Teil sollte nach dem Preprocessing angepasst werden <<

# Bitte tragen Sie im folgenden alle Grundstichwörte ein, welche Sie für die statistischen Auswertungen verwenden möchten.
# Grundstichwörter (gesamte Liste)
list_gs = [
        'Grundstichwort 1',
        'Grundstichwort 2',
        'Grundstichwort 3'
    ]

### für Hilfsfrist relevante Grundstichwörter
gs_hf = [
    'Grundstichwort 1',
    'Grundstichwort 2'
]

### für Notfallrettung relevante Grundstichwörter
gs_nr = [
    'Grundstichwort 1',
    'Grundstichwort 2'
]

#################### Zusätzliche Spalten ####################
# >> Anpassung ist nicht erforderlich <<
### !!! Die nachfolgenden Spalten nicht anpassen, diese werden durch das Tool erstellt / berechnet !!! ###
col_stichwort_bez = 'StichwortBez'      # Stichwort Bezeichnung
col_grundstichwort = 'Grundstichwort'   # Grundstichwort

col_hilfsfrist = 'Hilsfrist'

col_zeit_hilfsfrist = 'Zeit_Hilfsfrist'
col_zeit_hilfsfrist_em = 'Zeit_Hilfsfrist_EM'
col_zeit_anfahrt = 'Zeit_Anfahrt'
col_zeit_ausruecken = 'Zeit_Ausruecken'
col_zeit_versorgung = 'Zeit_Versorgung'
col_zeit_transport = 'Zeit_Transport'
col_zeit_ziel = 'Zeit_Ziel'
col_zeit_gesamt_pat = 'Zeit_gesamt_Patient'
col_zeit_gesamt = 'Zeit_gesamt'

col_s3_coord = 'S3_Koordinaten'
col_einsatz_coord = 'Einsatz_Koordinaten'
col_wache_coord = 'Wache_Koordinaten'

col_wache_lat = 'Wache_lat'
col_wache_lon = 'Wache_lon'

col_em_wache = 'EM_Wache'
col_wache = 'Wache'
col_em_rdb = 'RDB_des_EM'

col_rdb = 'RDB'

col_distance_einsatz = 'Distanz_zur_Einsatzstelle'
col_geschwindigkeit_anfahrt = 'Geschwindigkeit_Anfahrt'

#################### Parameter für Dateien ####################

# Paramter für Dateien:
file_stichwort = '../config/preprocessing/filter_stichwort.csv'
file_em_typ = '../config/preprocessing/filter_em_typ.csv'
file_matching_stichwort = '../config/preprocessing/filter_stichworte.csv'
file_wachen_coord = '../config/preprocessing/wachen_coord.csv'
