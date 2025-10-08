import json
import time
import requests

RUTA_ARCHIVO = "lista_pons.txt"
BLOQUE = 20  # Cambia esto según lo que aguante tu endpoint
URL = "http://localhost:8000/check/list"

def leer_por_bloques(path, tamaño):
    with open(path, "r") as archivo:
        bloque = []
        for linea in archivo:
            pon = linea.strip()
            if pon:
                bloque.append(pon)
                if len(bloque) == tamaño:
                    yield bloque
                    bloque = []
        if bloque:
            yield bloque

for i, bloque in enumerate(leer_por_bloques(RUTA_ARCHIVO, BLOQUE), 1):
    print(f"🔁 Enviando bloque {i} con {len(bloque)} PONs")
    payload = {"pons": bloque}
    try:
        response = requests.post(URL, json=payload)
        print(f"✅ [{response.status_code}] {response.text}")
    except Exception as e:
        print(f"❌ Error en bloque {i}: {e}")
    
    # Controlar la carga sobre el servidor
    time.sleep(2)
 