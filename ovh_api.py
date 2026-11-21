#!/usr/bin/env python3
"""OVH API v1 Aufruf mit den Keys aus dem OpenBot-Vault.

Nutzung:
  python3 ovh_api.py GET /me
  python3 ovh_api.py GET /domain/zone/smartflow-suhl.de/record
  python3 ovh_api.py POST /domain/zone/smartflow-suhl.de/refresh '{}'

Keys: OVH_APPLICATION_KEY, OVH_APPLICATION_SECRET, OVH_CONSUMER_KEY
Der Vault-Ordner wird automatisch gesucht; OVH_VAULT kann ihn überschreiben.
"""
import glob
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("OVH_ENDPOINT", "https://eu.api.ovh.com/1.0")
VAULT_GLOB = "/var/lib/openbot/.config/OpenBot/agent-api-keys/.vault/*"


def vault_dir():
    if os.environ.get("OVH_VAULT"):
        return os.environ["OVH_VAULT"]
    for d in glob.glob(VAULT_GLOB):
        if os.path.exists(os.path.join(d, "OVH_APPLICATION_KEY")):
            return d
    raise SystemExit("Kein OVH-Key im Vault gefunden (OVH_APPLICATION_KEY fehlt).")


def read(name):
    with open(os.path.join(vault_dir(), name)) as fh:
        return fh.read().strip()


def call(method, path, body=None):
    app_key = read("OVH_APPLICATION_KEY")
    app_secret = read("OVH_APPLICATION_SECRET")
    consumer_key = read("OVH_CONSUMER_KEY")

    url = BASE + path
    payload = json.dumps(body, separators=(",", ":")) if body else ""

    ts = str(int(time.time()))
    raw = "+".join([app_secret, consumer_key, method.upper(), url, payload, ts])
    sig = hashlib.sha1(raw.encode("utf-8")).hexdigest()

    headers = {
        "X-Ovh-Application": app_key,
        "X-Ovh-Consumer": consumer_key,
        "X-Ovh-Timestamp": ts,
        "X-Ovh-Signature": "$1$" + sig,
    }
    if payload:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=payload.encode("utf-8") if payload else None,
        headers=headers, method=method.upper()
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    method, path = sys.argv[1], sys.argv[2]
    body = json.loads(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
    status, text = call(method, path, body)
    print(status)
    print(text[:4000])