import re
import csv
import json
import sys


# ----------------------------
# Cargar técnicas desde CSV
# ----------------------------
def cargar_disarm(csv_file):
    disarm = {}

    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            tid = row.get("disarm_id", "").strip()
            name = row.get("name", "").strip()
            if tid:
                disarm[tid] = name

    return disarm


# ----------------------------
# Extraer técnicas del TXT
# ----------------------------
def extraer_tecnicas(txt_file):
    with open(txt_file, encoding="utf-8") as f:
        contenido = f.read()

    # Busca T0001 o T0001.001
    patron = r"T\d{4}(?:\.\d+)?"
    return set(re.findall(patron, contenido))


# ----------------------------
# Filtrar solo técnicas DISARM
# ----------------------------
def filtrar_tecnicas(tecnicas, disarm_dict):
    return sorted([t for t in tecnicas if t in disarm_dict])


# ----------------------------
# Construir JSON DISARM Navigator
# ----------------------------
def construir_json(tecnicas, disarm_dict):
    layer = {
        "version": "4.5",
        "name": "DISARM Layer",
        "domain": "disarm",
        "description": "Layer generado automáticamente desde Attack Flow",
        "filters": {
            "platforms": ["DISARM"]
        },
        "sorting": 0,
        "layout": {
            "layout": "side",
            "showID": True,
            "showName": True
        },
        "techniques": [],
        "gradient": {
            "colors": ["#ffffff", "#ff6666"],
            "minValue": 0,
            "maxValue": 1
        },
