import json
import csv
import sys
import os

def procesar_afb(file_path):
    nombre_base = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{nombre_base}.json"
    
    # 1. Cargar técnicas válidas de DISARM
    tecnicas_validas = set()
    try:
        with open('DISARM_Techniques.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                tecnicas_validas.add(row['disarm_id'])
    except FileNotFoundError:
        print("Error: No se encuentra 'DISARM_Techniques.csv'")
        return

    # 2. Leer fichero .afb
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tecnicas_encontradas = set()

    # Función recursiva para buscar estructuras "ttp" en objetos complejos
    def buscar_ttp(obj):
        if isinstance(obj, dict):
            if "ttp" in obj:
                # Extraer táctica y técnica según el formato solicitado
                # Estructura ejemplo: "ttp": [["tactic", "TA..."], ["technique", "T..."]]
                ttp_list = obj["ttp"]
                tecnica = None
                for item in ttp_list:
                    if isinstance(item, list) and len(item) == 2:
                        if item[0] == "technique":
                            tecnica = item[1]
                
                if tecnica and tecnica in tecnicas_validas:
                    tecnicas_encontradas.add(tecnica)
                    print(f"Técnica detectada: {tecnica}")
            
            for key, value in obj.items():
                buscar_ttp(value)
        elif isinstance(obj, list):
            for item in obj:
                buscar_ttp(item)

    # Iniciar búsqueda
    buscar_ttp(data)

    # 3. Crear estructura JSON para DISARM Navigator
    layer = {
        "name": nombre_base,
        "versions": {"attack": "1", "navigator": "4.8.2", "layer": "4.4"},
        "domain": "DISARM",
        "techniques": []
    }

    for t in tecnicas_encontradas:
        layer["techniques"].append({
            "techniqueID": t,
            "color": "#a1d99b",
            "enabled": True,
            "metadata": [],
            "showSubtechniques": True
        })

    # 4. Guardar resultado
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(layer, f, indent=4)
    
    print(f"\nFichero generado con éxito: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python convert_afb_to_disarm.py <fichero.afb>")
    else:
        procesar_afb(sys.argv[1])