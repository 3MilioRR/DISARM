import re
import csv
import json
import sys
import os


# ----------------------------
# 1. CARGAR CSV Y MOSTRARLO
# ----------------------------
def cargar_disarm(csv_file):
    disarm = {}

    print("\n=== [1] CARGA CSV ===")

    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')

        count = 0
        for row in reader:
            tid = row.get("disarm_id", "").strip()
            name = row.get("name", "").strip()

            if tid:
                disarm[tid] = name

                # mostramos primeras filas
                if count < 20:
                    print(f"{tid} -> {name}")

                count += 1

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
def construir_json(tecnicas, disarm_dict):

    layer = {
        "version": "4.5",
        "name": "DISARM Layer",
        "domain": "disarm",
        "description": "Layer generado desde builder",
        "filters": {
            "platforms": ["DISARM"]
        },
        "sorting": 0,
        "layout": {
            "layout": "side",
            "showID": True,
            "showName": True
        },
        "techniques": []
    }

    for t in tecnicas:
        layer["techniques"].append({
            "techniqueID": t,
            "techniqueName": disarm_dict[t],
            "score": 1
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

    if not os.path.exists(txt_file):
        print(" No existe el AFB")
        sys.exit(1)

    if not os.path.exists(csv_file):
        print(" No existe el CSV")
        sys.exit(1)

    # 1
    disarm_dict = cargar_disarm(csv_file)

    # 2
    encontradas = extraer_tecnicas(txt_file)

    # 3
    validas = filtrar_tecnicas(encontradas, disarm_dict)

    print("\n=== RESULTADO FINAL ===")
    for t in validas:
        print(f"{t} - {disarm_dict[t]}")

    print(f"\n Total válidas: {len(validas)}")

    json_data = construir_json(validas, disarm_dict)

    guardar(validas, json_data)

    print("\n Archivos generados")


if __name__ == "__main__":
    main()