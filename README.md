# Security_Projekt

## Projektübersicht
In diesem Projekt habe ich eine Umgebung mit Grafana und Influxb aufgebaut. Das Ziel ist es einen Lastentest zu machen auf Influxdb. Die Daten werden dann ausgewertet und mit den Grafanadashboards dargestellt. Dieses Projekt dient einer Angriffsimulation.

Die gesamte Umgebung läuft auf verschiedenen Ubunut-VM's die mit einem Vagrantfile erstellt wurden.

## Ziel des Projektes

1. Vagrantfile erstellen
2. Grafana, Mosquitto und Influxdb einrichten
3. Script für den Lastentest erstellen
4. Lastentest durchführen
5. Grafanadashboards erstellen

## Architektur

![Architektur](Grafana.png)

Das Projekt beinhaltet folgende Komponenten:

| Komponente | Aufgabe |
|------------|---------|
| **Vagrant** | Zum erstellen, verwalten und starten sowie stoppen der virtuellen Maschinen|
| **Grafana** | Zur grafischen Darstellung des Lastentests auf Influxdb |
| **Influxdb** | Zum speichern der Messdaten vom Lastentest   |
| **Lastenscript** | Zur Ausführen des Lastentest |

## Voraussetzungen

1. Git
2. Virtualbox oder Paralles
3. Vagrant 2.4 oder neuer
4. Mindestens 4GB Arbeitsspeicher
5. Mindestens 10GB RAM
6. Internentanbindung

## Installation und Konfiguaration

Als erstes kann das Vagrantfile aus meinem Git Repo geklont werden: 

Mit diesem File kann eine VM für Granfan und eine für Influxdb hochgezogen werden.



