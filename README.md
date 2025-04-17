# Simple Chord Implementation

## Projektstruktur

| Datei             | Beschreibung                                                             |
| ----------------- | ------------------------------------------------------------------------ |
| `address.py`      | Definiert die `Address`-Klasse mit `ip`, `port` und `id`.                |
| `addrToID.py`     | Generiert eine Hash-ID (SHA-1) aus einer IP-Adresse (oder IP:Port).      |
| `finger_table.py` | Erstellt die Finger Table mit Startpunkten und Platzhaltern für Nodes.   |
| `node.py`         | Zentrale Logik: Knoten-Verhalten, Stabilisierung, RPC.                   |
| `create_node.py`  | Einstiegspunkt: Startet einen neuen Node, optional mit bekanntem Knoten. |

---

## Ausführung

### Voraussetzungen

- Python 3.x
- Keine zusätzlichen Libraries notwendig (nur Standardbibliothek)

### Starten eines Knotens

```bash
python create_node.py <ip:port> [<known_ip:port>]
```

## Anpassungsmöglichkeiten

Im File `settings.py` befinden sich konstante Variablen, welche angepasst werden können.

- `RING_SIZE` ... Größe des Ringes in Bit
- `INTERVAL_TIME` ... Nach wie vielen Sekunden die Hintergrundtasks ausgeführt werden

## Debugging & Monitoring

- In regelmäßigen Abständen werden die Finger Table und die aktuellen Nachbarn (Successor / Predecessor) in der Konsole ausgegeben.

- Die print()-Ausgaben können bei Bedarf durch Logging ersetzt werden.
