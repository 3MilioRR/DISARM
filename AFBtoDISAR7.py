import re
import csv
import json
import sys
import os


# ----------------------------
# 1. CARGAR CSV,s Y MOSTRARLO
# ----------------------------

# CARGAR TACTICAS

def cargar_tacticas(csv_file):

    tacticas = {}

    print("\n=== [2] CARGA CSV TÁCTICAS ===")

    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')

        # DEBUG REAL
        print("CABECERAS RAW:", [repr(f) for f in reader.fieldnames])

        # NORMALIZAR CABECERAS
        reader.fieldnames = [
            f.replace("\\", "").replace("_", "_").strip()
            for f in reader.fieldnames
        ]

        print("CABECERAS NORMALIZADAS:", reader.fieldnames)

        for row in reader:

            # NORMALIZAR FILA
            row = {
                k.replace("\\", "").strip(): v
                for k, v in row.items()
            }

            # AHORA ESTO FUNCIONA SIEMPRE
            tid = row["tactic_id"].strip()
            name = row["tactic_name"].strip()

            tacticas[tid] = name

            print(f"✔ {tid} -> {name}")

    print(f"\n[+] Total tácticas cargadas: {len(tacticas)}")

    return tacticas

#  CARGAR TECNICAS

def cargar_disarm(csv_file):
    disarm = {}

    print("\n=== [1] CARGA CSV ===")

    try:
        with open(csv_file, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=';')

            print(f"[DEBUG] Cabeceras detectadas: {reader.fieldnames}")

            for i, row in enumerate(reader):
                tid = row["disarm_id"].strip()
                name = row["name"].strip()
                tactic = row["tactic_id"].strip()

                disarm[tid] = {
                    "name": name,
                    "tactic": tactic
                }


                # Mostrar primeras líneas para verificar
                if i < 10:
                    print(f"{tid} -> {name} ({tactic})")

    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        exit()

    print(f"\n[+] Total técnicas cargadas: {len(disarm)}")

    return disarm


# ----------------------------
# 2. EXTRAER TÉCNICAS DEL AFB
# ----------------------------
def extraer_tecnicas(txt_file):
    print("\n=== [2] PARSER AFB ===")

    with open(txt_file, encoding="utf-8") as f:
        contenido = f.read()

    # TU FORMATO EXACTO
    patron = r'\["technique_id","(T\d{4}(?:\.\d+)?)"\]'
    tecnicas = set(re.findall(patron, contenido))

    print(f"[+] Técnicas detectadas en AFB: {len(tecnicas)}")

    # mostrar todas para comprobar
    for t in tecnicas:
        print(f"ENCONTRADA -> {t}")

    return tecnicas


# ----------------------------
# 3. FILTRAR CONTRA CSV
# ----------------------------
def filtrar_tecnicas(tecnicas, disarm_dict):
    print("\n=== [3] FILTRADO ===")

    validas = []

    for t in tecnicas:
        if t in disarm_dict:
            print(f"✔ {t} EXISTE en CSV")
            validas.append(t)
        else:
            print(f"✘ {t} NO EXISTE en CSV")

    return sorted(validas)


# ----------------------------
# JSON final
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
# GUARDAR
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
        sys.exit(1)

    txt_file = sys.argv[1]
    csv_file = "DISARM_Techniques.csv"
    tactics_csv = "DISARM_Tactics.csv"   

    if not os.path.exists(txt_file):
        print("No existe el AFB")
        sys.exit(1)

    if not os.path.exists(csv_file):
        print("No existe el CSV de técnicas")
        sys.exit(1)

    if not os.path.exists(tactics_csv):
        print("No existe el CSV de tácticas")
        sys.exit(1)

    # 1. Cargar técnicas DISARM
    disarm_dict = cargar_disarm(csv_file)

    # 2. Cargar tácticas DISARM
    tactic_dict = cargar_tacticas(tactics_csv)

    # 3. Parsear AFB
    encontradas = extraer_tecnicas(txt_file)

    # 4. Filtrar
    validas = filtrar_tecnicas(encontradas, disarm_dict)

    print("\n=== RESULTADO FINAL ===")
    for t in validas:
        print(f"{t} - {disarm_dict[t]['name']}")

    print(f"\n Total válidas: {len(validas)}")

    # 5. Construir JSON (con tácticas ahora)
    json_data = construir_json(validas, disarm_dict, tactic_dict)

    # 6. Guardar
    guardar(validas, json_data)

    print("\n Archivos generados")