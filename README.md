# DISARM
Colección de ficheros de ejemplo para convertir flujos de AFB (ATT&amp;CK Flow Builder) en JSON de DISARM  

el proceso es el siguiente   
ficher.afb + app > disarm_layer.json + techniques_found.txt 

Para lanzar la aplicación:
```
python Convert_afb_to_DISARM.py Nombre-del-Fichero.afb
```

### Contenido del repo

Ficheros de la aplicación:   
1. Convert_afb_to_DISARM.py (programa que convierte ficheros afb en json)
2. DISARM_Tactics.csv (tabla maestra con las tácticas de DISARM)
3. DISARM_Techniques.csv (tabla maestra con las técnicas de DISARM)
4. Full_DISARM_Techniques.csv (tabla maestra completa de Técnicas para futuros usos de la aplicación)

Tambien se incluyen los siguientes ficheros de ejemplo para hacer una prueba de concepto    

5. Doppelganger.afb (Fichero generado con ATT&amp;CK Flow Builder, basado en la campaña Doppelganger y que queremos convertir en layer de Navigator)
6. disarm_layer.json (layer o capa generada por la app, lista para su carga en DISARM Navigator)
7. techniques_found.txt (por el mismo precio, la app saca el listado de las técnicas encontradas, por si ressulta útil tenerlas en txt)
8. Doppelanger_Manual.json (Layer de DISARM generado a mano en el Navigator que sirve como contraste o referencia del correcto funcionamiento de la app)




