import json
import csv
import sys
import os

def procesar_afb(file_path):
    nombre_base = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{nombre_base}.json"
    
    # 1. Cargar técnicas válidas de DISARM con manejo de encoding y delimitador
    tecnicas_validas = set()
    try:
        # 'utf-8-sig' elimina el BOM si existe, evitando el error de clave en la primera columna
        with open('DISARM_Techniques.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Usamos el método .get() para evitar KeyError y verificar que el ID no esté vacío
                disarm_id = row.get('disarm_id')
                if disarm_id:
                    tecnicas_validas.add(disarm_id)
    except FileNotFoundError:
        print("Error: No se encuentra el fichero 'DISARM_Techniques.csv'")
        return

    # 2. Leer fichero .afb
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer el fichero .afb: {e}")
        return

    tecnicas_encontradas = set()

    # Función recursiva mejorada para buscar estructuras "ttp"
    def buscar_ttp(obj):
        if isinstance(obj, dict):
            if "ttp" in obj:
                ttp_list = obj["ttp"]
                for item in ttp_list:
                    # Buscamos la pareja ["technique", "T0000"]
                    if isinstance(item, list) and len(item) == 2:
                        if item[0] == "technique":
                            tecnica = item[1]
                            if tecnica in tecnicas_validas:
                                if tecnica not in tecnicas_encontradas:
                                    tecnicas_encontradas.add(tecnica)
                                    print(f"Técnica detectada: {tecnica}")
            
            for key in obj:
                buscar_ttp(obj[key])
        elif isinstance(obj, list):
            for item in obj:
                buscar_ttp(item)

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
    
    print(f"\nProceso finalizado. Fichero generado: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <fichero.afb>")
    else:
        procesar_afb(sys.argv[1])