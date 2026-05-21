import json
import csv
import sys
import os

def procesar_afb(file_path):
    nombre_base = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{nombre_base}.json"
    
    # 1. Cargar técnicas válidas
    tecnicas_validas = set()
    try:
        with open('DISARM_Techniques.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row.get('disarm_id'):
                    tecnicas_validas.add(row['disarm_id'])
    except Exception as e:
        print(f"Error cargando CSV: {e}")
        return

    # 2. Leer .afb
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tecnicas_encontradas = set()

    # 3. Analizar la estructura específica de .afb (attack_flow_v2)
    # Los datos están en data["objects"]
    if "objects" in data:
        for obj in data["objects"]:
            # Cada objeto tiene una lista de propiedades
            if "properties" in obj:
                for prop in obj["properties"]:
                    # Buscamos la propiedad que sea una lista y empiece por "ttp"
                    if isinstance(prop, list) and len(prop) > 0 and prop[0] == "ttp":
                        ttp_data = prop[1] # Esto es la lista interna de táctica/técnica
                        
                        # Buscamos "technique" dentro de ttp_data
                        for item in ttp_data:
                            if isinstance(item, list) and len(item) == 2 and item[0] == "technique":
                                tecnica = item[1]
                                if tecnica in tecnicas_validas:
                                    if tecnica not in tecnicas_encontradas:
                                        tecnicas_encontradas.add(tecnica)
                                        print(f"Técnica detectada: {tecnica}")

    if not tecnicas_encontradas:
        print("No se encontraron técnicas de DISARM en el fichero. Verifica que las técnicas en el .afb coincidan exactamente con los IDs del CSV.")
        return

    # 4. Generar JSON
    layer = {
        "name": nombre_base,
        "versions": {"attack": "1", "navigator": "4.8.2", "layer": "4.4"},
        "domain": "DISARM",
        "techniques": [{"techniqueID": t, "color": "#a1d99b", "enabled": True, "metadata": [], "showSubtechniques": True} 
                       for t in tecnicas_encontradas]
    }

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(layer, f, indent=4)
    
    print(f"\nFichero generado: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <fichero.afb>")
    else:
        procesar_afb(sys.argv[1])