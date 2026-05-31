import re
import csv
import json
import sys
import os


# ----------------------------
# CARGAR TECNICAS DISARM
# ----------------------------
def cargar_disarm(csv_file):
    disarm = {}

    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            tid = row["disarm_id"].strip()
            name = row["name"].strip()
            tactic = row["tactic_id"].strip()

            disarm[tid] = {
                "name": name,
                "tactic": tactic
            }

    return disarm


# ----------------------------
# CARGAR TACTICAS DISARM
# ----------------------------
def cargar_tacticas(csv_file):
    tactics = {}

    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            tid = row["tactic_id"].strip()
            name = row["tactic_name"].strip()

            tactics[tid] = name

    return tactics


# ----------------------------
# EXTRAER TECNICAS DEL AFB
# ----------------------------
def extraer_tecnicas(afb_file):
    with open(afb_file, encoding="utf-8") as f:
        contenido = f.read()

    patron = r'\["technique_id","(T\d{4}(?:\.\d+)?)"\]'
    tecnicas = set(re.findall(patron, contenido))

    return tecnicas


# ----------------------------
# FILTRAR
# ----------------------------
def filtrar_tecnicas(tecnicas, disarm_dict):
    return sorted([t for t in tecnicas if t in disarm_dict])


# ----------------------------
# CONSTRUIR JSON (VALIDO)
# ----------------------------
def construir_json(tecnicas, disarm_dict, tactic_dict):

    layer = {
        "name": "DISARM Layer",
        "versions": {
            "attack": "1",
            "navigator": "4.8.2",
            "layer": "4.4"
        },
        "domain": "DISARM",
        "description": "Generado automáticamente",
        "filters": {
            "platforms": ["Windows", "Linux", "Mac"]
        },
        "sorting": 0,
        "layout": {
            "layout": "side",
            "aggregateFunction": "average",
            "showID": False,
            "showName": True,
            "showAggregateScores": False,
            "countUnscored": False
        },
        "hideDisabled": False,
        "techniques": [],
        "gradient": {
            "colors": ["#ff6666ff", "#ffe766ff", "#8ec843ff"],
            "minValue": 0,
            "maxValue": 100
        },
        "legendItems": [],
        "metadata": [],
        "links": [],
        "showTacticRowBackground": False,
        "tacticRowBackground": "#dddddd",
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False
    }

    for t in tecnicas:
        tactic_id = disarm_dict[t]["tactic"]
        tactic_name = tactic_dict.get(tactic_id, "unknown")

        layer["techniques"].append({
            "techniqueID": t,
            "tactic": tactic_name,
            "color": "#fc6b6b",
            "comment": "",
            "enabled": True,
            "metadata": [],
            "links": [],
            "showSubtechniques": False
        })

    return layer


# ----------------------------
# GUARDAR RESULTADOS
# ----------------------------
def guardar(tecnicas, json_data):

    with open("techniques_found.txt", "w", encoding="utf-8") as f:
        for t in tecnicas:
            f.write(t + "\n")

    with open("disarm_layer.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


# ----------------------------
# MAIN
# ----------------------------
def main():

    if len(sys.argv) != 2:
        print("Uso: python script.py fichero.afb")
        return

    afb_file = sys.argv[1]
    csv_file = "DISARM_Techniques.csv"
    tactics_csv = "DISARM_Tactics.csv"

    if not os.path.exists(afb_file):
        print("❌ No existe el fichero AFB")
        return

    if not os.path.exists(csv_file):
        print("❌ No existe DISARM_Techniques.csv")
        return

    if not os.path.exists(tactics_csv):
        print("❌ No existe DISARM_Tactics.csv")
        return

    # Cargar datos
    disarm_dict = cargar_disarm(csv_file)
    tactic_dict = cargar_tacticas(tactics_csv)

    # Extraer técnicas
    encontradas = extraer_tecnicas(afb_file)

    # Filtrar
    validas = filtrar_tecnicas(encontradas, disarm_dict)

    # Mostrar por pantalla
    print("\n=== TECNICAS ENCONTRADAS ===")
    for t in validas:
        print(f"{t} - {disarm_dict[t]['name']}")

    print(f"\nTotal: {len(validas)}")

    # Construir JSON
    json_data = construir_json(validas, disarm_dict, tactic_dict)

    # Guardar
    guardar(validas, json_data)

    print("\n✅ Generados:")
    print("- techniques_found.txt")
    print("- disarm_layer.json")


if __name__ == "__main__":
    main()