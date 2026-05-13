import re
import csv
import json
import sys
from pathlib import Path


def load_disarm_ids(csv_file):
    disarm_ids = set()

    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row.get("disarm_id"):
                disarm_ids.add(row["disarm_id"].strip())

    return disarm_ids


def extract_techniques(txt_file):
    with open(txt_file, encoding="utf-8") as f:
        content = f.read()

    # Buscar IDs tipo T0001 o T0001.001
    pattern = r"T\d{4}(?:\.\d+)?"
    found = set(re.findall(pattern, content))

    return found


def filter_valid_techniques(found, valid_ids):
    return sorted([t for t in found if t in valid_ids])


def generate_navigator_json(techniques):
    # Formato compatible con ATT&CK Navigator (adaptado a DISARM)
    layer = {
        "version": "4.3",
        "name": "DISARM Layer",
        "domain": "disarm",
        "description": "Generated from Attack Flow",
        "techniques": [],
        "gradient": {
            "colors": ["#ffffff", "#66b1ff"],
            "minValue": 0,
            "maxValue": 1
        },
        "legendItems": [],
        "metadata": [],
        "links": []
    }

    for t in techniques:
        layer["techniques"].append({
            "techniqueID": t,
            "score": 1
        })

    return layer


def save_outputs(techniques, json_data):
    # TXT
    with open("techniques_found.txt", "w", encoding="utf-8") as f:
        for t in techniques:
            f.write(t + "\n")

    # JSON
    with open("disarm_layer.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def main():
    if len(sys.argv) < 2:
        print("Uso: python script.py <archivo_txt>")
        sys.exit(1)

    txt_file = sys.argv[1]
    csv_file = "DISARM_Techniques.csv"

    if not Path(txt_file).exists():
        print("Error: el archivo txt no existe")
        sys.exit(1)

    if not Path(csv_file).exists():
        print("Error: el CSV no existe")
        sys.exit(1)

    print("[+] Cargando técnicas DISARM...")
    disarm_ids = load_disarm_ids(csv_file)

    print("[+] Extrayendo técnicas del flujo...")
    found = extract_techniques(txt_file)

    print("[+] Filtrando técnicas válidas...")
    techniques = filter_valid_techniques(found, disarm_ids)

    print("\n=== Técnicas encontradas ===")
    for t in techniques:
        print(t)

    print(f"\nTotal: {len(techniques)} técnicas")

    print("[+] Generando JSON para Navigator...")
    json_data = generate_navigator_json(techniques)

    print("[+] Guardando resultados...")
    save_outputs(techniques, json_data)

    print("\n✅ Archivos generados:")
    print("- techniques_found.txt")
    print("- disarm_layer.json")


if __name__ == "__main__":
    main()
