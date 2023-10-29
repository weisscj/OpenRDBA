# Preprocessing
## 1. Preparation (prepapration.py)
Führen Sie die Datei "preparation.py" aus und übergeben Sie den Pfad zu ihrem Datensatz. Vom Skript wird ein Datensatz im csv Format erwartet, welcher ein Semikolon als Trennzeichen verwendet. Die erste Zeile muss die Spaltennamen enthalten.

```bash
python3 preparation.py ordner/data.csv
```

Das Skript erstellt alle benötigten Ordner und lädt zusätzliche Datensätze zu den Kommunen herunter. Für den Datensatz werden Übersichten über die enthaltenen Stichwörter, Einsatzmitteltypen und Spalten erstellt. Während der Ausführung werden Sie aufgefordet die Namen der Spalten "Stichwörter" und "Einsatzmitteltypen" anzugeben.

Führen Sie nach erfolgreicher Ausführung die nachfolgenden Schritte aus:

### 1.1 Konfiguration anpassen
Öffnen Sie die Datei "config/config.py" in einem Texteditor und passen Sie die Parameter gemäß Ihren Daten und gesetzlichen Vorgaben zur Hilfsfrist an. Normalerweise befinden sich in einem Datensatz auch Zellen, welche keinen Inhalt haben, bzw. einen Wert für "keinen Inhalt" , z.B. "-" besitzen. Dieses Wert müssen Sie in der Variable "nan_value" angeben.

Im Abschnitt "Spaltennamen im Datensatz" müssen Sie die Namen der Spalten Ihres Datensatzes angeben. Eine Übersicht über die erkannten Spalten in Ihrem Datensatz finden Sie in der Datei "config/preparation/output_spalten.csv".

Im Abschnitt "Paramter für Clustering (create_regions.py)" können Sie die Paramter für die Generierung von kleinen Regionen anpassen. Wenn Sie das Tool zum ersten Mal ausführen können Sie dies zurückstellen und sich zuerst mit der vollen Funktionalität vertraut machen.

### 1.2 Filtern von Rettungsdienstbereichen
Legen Sie im Ordner "config/preprocessing/" eine Datei mit dem Namen "filter_em_rdb.csv an". Geben Sie in diesem Dokument in der ersten Spalte an, welche Rettungsdienstbereiche Sie verwenden möchten. Geben Sie in der zweiten Spalte einen vollständigen Namen für den Rettungsdienstbereich an. Die Zuordnung erfolgt über den Funkrufnamen eines Einsatzmittels. 

Beispiel für die Datei:
|RDB (Funkruf)|RDB ausgeschrieben|
|---|---|
|RN | Rhein-Neckar|
|MA | Mannheim|
|KA | Karlsruhe|

Die Datei benötigt keinen Header. Trennzeichnen ist ein Semikolon.

### 1.3 Filtern von Einsatzmitteltypen
Legen Sie im Ordner "config/preprocessing/" eine Datei mit dem Namen filter_em_typ.csv an. Geben Sie in diesem Dokument in der ersten Spalte an, welche Einsatzmitteltypen Sie verwenden möchten.

Eine Übersicht über die erkannten Einsatzmitteltypen inklusive Häufigkeit des Vorkommens in Ihrem Datensatz finden Sie in der Datei "config/preparation/output_em_typ.csv". 

Beispiel für die Datei:
|EM_Typ|
|---|
|RTW|
|KTW|
|NEF|

Hinweis: Die Datei benötigt keinen Header. Trennzeichnen ist ein Semikolon.

### 1.4 Filtern von Stichwörtern
Legen Sie im Ordner "config/preprocessing/" eine Datei mit dem Namen "filter_stichworte.csv an". Geben Sie in diesem Dokument in der ersten Spalte an, welches Stichwort Sie verwenden möchten. Geben Sie in der zweiten Spalte eine Beschreibung des Stichwortes an. Geben Sie in der dritten Spalte ein zugehöriges Grundstichwort an.

Eine Übersicht über die erkannten Stichwörter inklusive Häufigkeit des Vorkommens in Ihrem Datensatz finden Sie in der Datei "config/preparation/output_stichwort.csv". 


Beispiel für die Datei:
| Stichwort | Beschreibung | Grundstichwort |
|---|---|---|
124 A | Schlechter AZ | RD2 |
124 B | Schlechter AZ | RD1 |
124 C | Schlechter AZ | RD0 |

Hinweis: Die Datei benötigt keinen Header. Trennzeichnen ist ein Semikolon.

Zum aktuellen Zeitpunkt ist es nicht möglich auf Grundlage einer Salte in Ihrem Datensatz evtl. vorhanden Grundstichwörter auszulesen. Sollten Sie Grundstichwörter in Ihrem Datensatz haben, so müssen Sie diese zum aktuellen Zeitpunkt noch manuelle angeben.

### 1.5 Hinzufügen von Koordinaten der Rettungswachen
Legen Sie im Ordner "config/preprocessing/" eine Datei mit dem Namen "wachen_coord.csv an". Geben Sie in diesem Dokument in der ersten Spalte an, welchen Funkrufnamen die entsprechende Wache hat. Geben Sie in der zweiten Spalte die Latitude an. Geben Sie in der dritten Spalte die Longitude an.

| Funkrufname | Lat | Lon |
|-------------|-----|-----|
| RN 1/83 | 49.123 | 8.123 |

Hinweis: Die Datei benötigt keinen Header. Trennzeichnen ist ein Semikolon.

Bitte öffen Sie die nach erfolgreicher Ausführung die erstellten Dokumente. Öffen Sie außerdem die Datei config/config.py sowie die filter Dateien (siehe [Dokumentation]()) und passen Sie die Parameter an Ihren Datensatz an.

## 2. Preprocessing (preprocessing.py)
Wenn Sie die das Skript preparation.py erfolgreich ausgeführt haben, die Datei config.py sowie die Filter Dateien angepasst haben, können Sie mit dem preprocessing beginnen. Das Skript preprocessing.py bereitet die Daten für die Analyse vor. Neben dem Unwandeln von Datentypen werden die Daten basierend auf den Filterkriterien gefiltet. Bitte beachten Sie, dass die Ausführung des Skriptes je nach Umfang Ihres Datensatzes mehrere Minuten dauern kann.

```bash
python3 preprocessing.py ordner/data.csv
```

Nach der Filterung und Aufbereitung des Datensatzes wird eine Kopie im Ordner data/ gepeichert. Im Ordner config werden die Dateien "output_RDB_des_EM.csv" und "output_Stichwort.csv" erstellt, welche einen ersten Überblick über den Datensatz nach Filterung ermöglichen.

## 3. Generierung von Regionen (create_regions.py)
Eine reine Verwendung von Kommunen für eine Fahrzeitanalyse ist aufgrund der Größe dieser nicht sinnvoll. Hierzu ist es erforderlich kleine und logisch zusammehängnde Regionen zu generieren, welche deutlich kleiner als Kommunen sind. Dies geschieht durch die Verwendung von Daten aus [OpenStreetMap](https://www.openstreetmap.org/copyright) (OSM), welche über die Tags 'landuse' verfügen. Um die Qualität dieser Regionen für die beabsichtigte Verwendung zu erhöhen, werden Einsätze identifiziert, die außerhalb der Polygone liegen. Diese Outlier werden mithilfe eines DBSCAN-Algorithmus zu Clusern zusammengefasst. Diese Cluster werden anschließend zu den OSM Daten hinzugefügt. Um zu gewährleisten, dass die entstehenden Regionen nicht zu groß werden, werden die Polygone an den kommunalen Grenzen zerschnitten.

Aktuell müssen Sie ein geopackage mit den Polygonen für Ihren Rettungsdienstbereich und die umliegenden Rettungsdienstbereiche unter data/regions/rdb.gpkg ablegen. Zusätzlich wird unter data/grenzen_all.gpkg ein geopackage mit den kommunalen Grenzen für Ihren Bereiche benötigt. Dieses wird verwendet, um die kleinen Regionen die für die Fahrzeitanalyse erstellt werden an den Grenzen zu zerschneiden. Es ist geplant, dass diese Schritte in zukünftigten Versionen zu automatisieren. Sollten Sie Fragen oder Probleme haben, erstellen Sie bitte ein Issue.

Eine Veränderung der Paramter ist über eine [Anapssung der Konfiguration](#1-konfiguration-anpassen) möglich.

```bash
python3 create_regions.py
```

Für weitergehende Informationen zu den OpenStreetMap Daten besuchen Sie bitte das OSM Wiki unter [https://wiki.openstreetmap.org/wiki/Land_use](https://wiki.openstreetmap.org/wiki/Land_use)

Der Download der OSM Daten erfolgt über die ohsome API, bzw. über das Package ohsome-py. Weitere Informationen finden Sie unter [https://github.com/GIScience/ohsome-api](https://github.com/GIScience/ohsome-api) und unter [https://github.com/GIScience/ohsome-py](https://github.com/GIScience/ohsome-py)