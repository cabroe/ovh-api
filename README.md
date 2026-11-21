# ovh-api

Ein Skript für die OVH-API v1: ruft mit den Keys aus dem OpenBot-Vault beliebige Endpunkte auf. Gedacht für DNS-Pflege und schnelle Prüfungen, ohne Klick im OVH-Manager.

Keine Zugangsdaten im Repo: das Skript liest sie zur Laufzeit aus dem Vault.

## Voraussetzungen

Drei Werte als Dateien im Vault-Verzeichnis (ohne Zeilenumbruch):

| Datei | Inhalt |
|---|---|
| `OVH_APPLICATION_KEY` | Application Key der OVH-API-App |
| `OVH_APPLICATION_SECRET` | Application Secret |
| `OVH_CONSUMER_KEY` | Consumer Key mit den nötigen Rechten |

Gesucht wird standardmäßig unter `/var/lib/openbot/.config/OpenBot/agent-api-keys/.vault/*`; das erste Verzeichnis mit `OVH_APPLICATION_KEY` gewinnt. Ein anderer Ort lässt sich setzen:

```bash
export OVH_VAULT=/pfad/zum/vault
```

Anderer Endpunkt, etwa für ein anderes Rechenzentrum:

```bash
export OVH_ENDPOINT=https://ca.api.ovh.com/1.0
```

Nur Python 3, keine Abhängigkeiten.

## Nutzung

```bash
python3 ovh_api.py GET  /me
python3 ovh_api.py GET  /domain/zone/example.de/record
python3 ovh_api.py POST /domain/zone/example.de/refresh '{}'
```

Argumente: Methode, Pfad, optional ein JSON-Body. Ausgabe: HTTP-Status in der ersten Zeile, danach die Antwort (gekürzt auf 4000 Zeichen). Ein HTTP-Fehler ist kein Skriptfehler: das Skript gibt den Status aus und endet mit 0.

## Wie die Signatur funktioniert

Die v1-API signiert jede Anfrage mit SHA-1 über

```
AS + "+" + CK + "+" + METHODE + "+" + URL + "+" + BODY + "+" + TIMESTAMP
```

und schickt das Ergebnis als `X-Ovh-Signature: $1$<hash>` mit `X-Ovh-Application`, `X-Ovh-Consumer` und `X-Ovh-Timestamp`. Der Body muss exakt so signiert werden, wie er gesendet wird — deshalb serialisiert das Skript ihn einmal und nutzt denselben String für Hash und Request.

## Grenzen

- Ein Consumer Key gilt nur für die Zonen und Endpunkte, die bei der Freigabe angehakt wurden. Weitere Domains brauchen einen eigenen Key.
- Die Uhr des Rechners muss ungefähr stimmen, sonst weist die API den Timestamp ab.
- Schreibende Aufrufe (`POST`, `PUT`, `DELETE`) sind sofort wirksam; vorher mit `GET` prüfen.

## Herkunft

Entstanden im OpenBot-Team für die DNS-Zone `smartflow-suhl.de`. Die Datei ist identisch mit `OpenBot/Shared/scripts/ovh_api.py` auf dem OpenBot-Rechner.