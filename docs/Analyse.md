# Durchführen einer Analyse

**Hinweis:** Vor der Durchführung einer Analyse ist es erforderlich das [Preprocessing](#Preprocessing) erfolgreich durchgeführt zu haben! Alle Analyse Skripte greifen auf die im Preprocessing generierte Datei "data/data.pkl" zu. Eine Übergabe von Parametern ist beim Aufruf somit nicht erforderlich.

## 2.1 Gesamtstatistik (stats_gesamt.py)
Mithilfe des Skriptes stats_gesamt.py haben Sie die Möglichkeit folgende Statistiken zu generieren:

* Gesamtstatistik (in Abhängigkeit eines Jahres)
    * Auswertung Grundstichwörter
    * Auswertung Einsatzmittel
    * Auswertung Einsätze nach Rettungsdienstbereichen
    * Auswertung Einsatzmittel nach Rettungsdienstbereichen
    * Auswertung Fehleinsätze

* Zeitliche Auswertung (gesamter Zeitraum, pro Jahr, Monat, Tag, Stunde)
    * Zeitliche Auswertung Grundstichwörter
    * Zeitliche Auswertung Einsatzmitteltypen
    * Zeitliche Auswertung Fehleinsätze
    * Zeitliche Auswertung Stichwörter

* Zeitliche Auswertung über Woche
    * Grundstichwörter
    * Einsatzmitteltypen
    * Stichwörter

Jede Statistik wird als Plot generiert, welcher direkt angezeigt wird und abgespeichert werden kann. zusätzlich werden die Ergebnisse in die Konsole ausgegeben und als csv Datei gespeichert. Über ein Menü haben Sie die Möglichkeit zu definieren, welche Paramter Sie verwenden mäöchten.

```bash
python3 stats_gesamt.py
```

## 2.2 Statistik für Kommunen (stats_kommunen.py)
Das Skript stats_kommunen.py berechnet für Jedes Jahr, welches im Datensatz gefunden wird die Hilfsfrist und den Anteil der unterversorgten Bevölkerung. Zusätzlich werden Statistiken für jede Kommune berechnet. Die Ergebnisse werden als interaktive Karte in einem html Dokument, sowie als csv und geopackage gespeichert.
Wenn mehrer Jahre im Datensatz gefunden werden, werden zusätzlich die Differenzen zwischen dem ersten und dem letzten Jahr berechnet. Die Ergebnisse werden als html, csv und geopackage Datei gespeichert.

```bash
python3 stats_kommunen.py
```

## 2.3 Feinräumige Analyse (stats_region.py)
Mithilfe des Skriptes stats_region.py sind Sie in der Lage eine Fahrzeitanalyse durchzuführen. Sie können dabei nach dem Aufruf des Skriptes auswählen, ob Sie eine gesamte Analyse durchführen möchten, ob Sie eine spezifische Rettungswache analysieren möchten, oder ob Sie die Versorgungszeit (Alarm bis Ankuft Zielort) für ein spezifisches Stichwort oder Grundstichwort berechnen möchten. Gespeichert werden die Ergebnisse als html, csv und geopackage Datei.

```bash
python3 stats_regions.py
```
