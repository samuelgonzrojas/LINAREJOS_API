# api.py

from datetime import datetime
import json
from typing import List
from fastapi import APIRouter, HTTPException
from time import sleep
import logging
import asyncio
from classes.linarejos import LIN_DIAGNOSER

# initialización de router api
api = APIRouter()

KPI = "KPI#5"


# Función que procesa un solo PON
def process_pon_sync(pon: str):
    logging.info(f"Procesando {pon} para {KPI}")

    record_values = {
        "PON": pon,
        "KPI": KPI,
        "DESCRIPCION": "Test new KPI",
        "DATE": datetime.now(),
    }

    record = LIN_DIAGNOSER(**record_values)
    record.get_oid()

    sleep(record.wait)

    response = record.get_kpi()
    return {
        "PON": pon,
        "KPI_RESPONSE": response,
    }


# Envoltorio asíncrono
async def process_pon(pon: str):
    return await asyncio.to_thread(process_pon_sync, pon)


@api.post("/check/list")
async def check_pon_list(pons: List[str]):
    if not pons:
        raise HTTPException(status_code=400, detail="Empty PON list")

    tasks = []

    for i, pon in enumerate(pons):
        print(f"MAIN - PRO - {pon} - {i+1}/{len(pons)}")
        tasks.append(process_pon(pon))
        await asyncio.sleep(3)

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Guardar resultados en un archivo
    filename = f"save_list.json"
    with open(filename, "a") as f:
        json.dump(responses, f, default=str)

    logging.info(f"MAIN - SAVE")

    return HTTPException(status_code=200, detail="Diagnostico completo.")


# Nuevo Endpoint para procesar un solo PON
@api.get("/check/{pon}")
async def check_single_pon(pon: str):
    if not pon:
        raise HTTPException(status_code=400, detail="Empty PON")

    # Procesar el PON
    response = await process_pon(pon)

    # Guardar resultados en un archivo
    filename = f"{pon}_{KPI}.json"
    with open(filename, "w") as f:
        json.dump([response], f, default=str)

    logging.info(f"MAIN - SAVE")

    return HTTPException(status_code=200, detail=f"Diagnostico completo para {pon}.")
