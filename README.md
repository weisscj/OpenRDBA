# Rettungsdienstbereich Analyse
Die Analyse von Rettungsdienstbereichen in Deutschland erfolgt meist durch Strukturgutachten und aufwändige Analysen. Im Rahmen einer Bachelorarbeit am [Heidelberg Institute for Geoinformation Technology](https://heigit.org/de/willkommen/)
der Universität Heidelberg in Kooperation mit der [Integrierten Leitstelle Heidelberg/Rhein-Neckar-Kreis gGmbH](https://leitstelle-hd-rnk.de/) entstand dieses Tool welches eine Grundlegende Analyse eines Rettungsdienstbereiches durchführen kann. Das Tool führt auf Grundlage eines Datensatzes einer Leitstelle eine automatisierte Analyse durch und erstellt eine Reihe von Statistiken und Plots und interaktiven Karten. Besonderer Fokus liegt dabei auf einer räumlichen Auswertung. Da echte Einsatzdaten für die Analyse benötigt werden, richtet es sich an Leitstellen und Beschäftigte in Forschungseinrichtungen, welche über offizielle Datensätze verfügen. Besonderheit ist die Möglichkeit zu analysieren, wie schnell ein Einsatzmittel eine bestimmte Region erreichen kann. Dies geschieht nicht durch einen theoretische Berechnung mithilfe von Isochronen oder ähnlichen Methoden, sondern durch die Verwendung von Einsatdaten und der Generierung kleiner Regionen. Das Tool kann von Leitstellen und anderen Benutzer frei verwendet und auch abgewandelt werden. Bitte beachten Sie die Lizenzbestimmungen und lesen Sie vor der Verwendung sorgfältig die Dokumentation.

*Hinweis: Ein Testdatensatz ist in diesem Tool nicht enthalten und kann nicht zur Verfügung gestellt werden.*

## Features
* Preprocessing der Einsatzdaten
* Erstellung von Statistiken (Auswertung zu Grundstichwörtern, Einsatzmitteln, Einsätzen nach Rettungsdienstbereichen, Fehleinsätze, umfangreiche Zeitliche Auswertungen)
* Berechnung der eingehaltenen Hilfsfrist, Hilfsfristveränderungen, Anteil der unterversorgten Bevölkerung
* Erstellung von interaktiven Karten auf kommunaler Ebene (Hilfsfristauswertung, Entwicklung von Einsätzen/ Hilfsfristeinhaltungen etc.)
* Erstellung von interaktiven Karten auf feinräumiger Ebene

## Systemanforderungen und Abhängigkeiten
Die Anforderungen an die Hardware hängen stark vom Unfang des Datensatzes ab. Die Entwicklung und erfolgreiche Ausführung erfolgten auf einem System mit 16 GiB RAM und einem Intel® Core™ i7-1185G7 (11th Gen, 3.00GHz × 8) unter Ubuntu 22.04.3 LTS (64-bit). Abhängig vom Datensatz können höhere (bzw. niedrigere) Anforderungen erforderlich sein, jedoch werden mindestens 16 GiB RAM empfohlen.

Die Entwicklung erfolgte unter der Python Version 3.11.3. Verwendete Packete werden nachfolgende gelistet. Grundsätzlich können auch ältere oder neuere Versionen funktionieren, getestet wurde dies zum aktuellen Zeitpunkt nicht. Die Verwendung von anderen Versionen kann potenziell zu Fehlern führen, sollte jedoch die Berechnung von Ergebnissen nicht beeinflussen.

|package | version |
|--------|---------|
|numpy | 1.24.3 |
|matplotlib | 3.7.1 |
|seaborn | 0.12.2 |
|pandas | 1.5.3 |
|geopandas | 0.12.2 |
|folium | 0.14.0 |
|gdal | 3.6.3 |
|ohsome | 0.2.0 |
|scikit-learn | 1.2.2 |

## Installation
Clonen Sie das Repository und installieren Sie die benötigten packages. Empfohlen wird die Verwendung von [Anaconda](https://www.anaconda.com/download). Einzelne Packages wie [ohsome-py](https://github.com/GIScience/ohsome-py) müssen Sie unter Umständen mihilfe von pip installieren.

## Durchführung der Analyse
Die Durchführung einer Analyse erfolgt in zwei Schritten. Zunächst müssen Sie die Daten Aufbereiten, Filtern und die Konfiguration auf Ihren Datensatz anpassen. Sobald dies erfolgt ist und Sie über einen aufbereiteten Datensatz verfügen, können Sie im zweiten Schritt mit der eigentlichen Analyse starten.

* [Anleitung Preprocessing](docs/Preprocessing.md)
* [Anleitung Analyse](docs/Analyse.md)

## License
Diese Software ist lizensiert unter der GNU GPL 3.0. Eine Kopie der Lizenz finden Sie unter [LICENSE](LICENSE).

## Verwendete Datensätze
Dieses Tool verwendet mehrere Datensätze, welche während der Ausführung heruntergeladen werden. Bitte beachten Sie die Lizenzbestimmungen:

Datensatz zu Lokalen Verwaltungseinheiten (LAU):<br>
[DE: © EuroGeographics bezüglich der Verwaltungsgrenzen](https://ec.europa.eu/eurostat/de/web/gisco/geodata/reference-data/administrative-units-statistical-units/lau)

OpenStreetMap Daten:<br>
[OpenStreetMap Contributors](https://www.openstreetmap.org/copyright)