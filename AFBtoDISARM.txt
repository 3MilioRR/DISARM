import re
import csv
import json
import sys
import os


# ----------------------------
# Cargar técnicas DISARM
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
# NUEVO extractor compatible con builder DISARM
# ----------------------------
def extraer_tecnicas(txt_file):
    with open(txt_file, encoding="utf-8") as f:
        contenido = f.read()

    tecnicas = set()

    #  FORMATO NUEVO (el tuyo)
    patron_nuevo = r'\["technique_id","(T\d{4}(?:\.\d+)?)"\]'
    matches_nuevo = re.findall(patron_nuevo, contenido)
    tecnicas.update(matches_nuevo)

    #  FORMATO ANTIGUO (por si acaso)
    patron_antiguo = r'T\d{4}(?:\.\d+)?'
    matches_antiguo = re.findall(patron_antiguo, contenido)
    tecnicas.update(matches_antiguo)

    return tecnicas


# ----------------------------
# Filtrar válidas
# ----------------------------
def filtrar_tecnicas(tecnicas, disarm_dict):
    return sorted([t for t in tecnicas if t in disarm_dict])


# ----------------------------
# JSON DISARM Navigator
# ----------------------------
def construir_json(tecnicas, disarm_dict):
    layer = {
        "version": "4.5",
        "name": "DISARM Layer",
        "domain": "disarm",
        "description": "Generado desde Flow Builder DISARM",
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
            "score": 1,
            "color": "#ff6666",
            "enabled": True
        })

    return layer


# ----------------------------
# Guardar salida
# ----------------------------
def guardar(tecnicas, data):
    with open("techniques_found.txt", "w", encoding="utf-8") as f:
        for t in tecnicas:
            f.write(t + "\n")

    with open("disarm_layer.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# MAIN
# ----------------------------
def main():
    if len(sys.argv) != 2:
        print("Uso: python script.py fichero.txt")
        sys.exit(1)

    txt_file = sys.argv[1]
    csv_file = "DISARM_Techniques.csv"

    if not os.path.exists(txt_file):
        print(" TXT no encontrado")
        sys.exit(1)

    if not os.path.exists(csv_file):
        print(" CSV no encontrado")
        sys.exit(1)

    print("[+] Cargando DISARM...")
    disarm_dict = cargar_disarm(csv_file)

    print("[+] Extrayendo técnicas...")
    encontradas = extraer_tecnicas(txt_file)
    print(f"[+] Detectadas: {len(encontradas)}")

    print("[+] Filtrando...")
    validas = filtrar_tecnicas(encontradas, disarm_dict)

    print("\n=== RESULTADO ===")
    for t in validas:
        print(f"{t} - {disarm_dict[t]}")

    print(f"\n Total válidas: {len(validas)}")

    json_data = construir_json(validas, disarm_dict)

    guardar(validas, json_data)

    print("\n Archivos generados:")
    print("- techniques_found.txt")
    print("- disarm_layer.json")


if __name__ == "__main__":
    main()