# main.py

from datetime import datetime
import os
from fastapi import FastAPI
from time import sleep
import logging
from linarejos import LIN_DIAGNOSER
import uvicorn
from dotenv import load_dotenv

load_dotenv()


# inicialización de app FastAPI
app = FastAPI()


# Ping
@app.get("/ping")
def ping():
    return "OK"


@app.post("/check/{PON}")
def check_pon(PON: str):
    KPI = "KPI#1#5"

    if PON is None or not KPI.startswith("KPI#"):
        return "Datos incorrectos"

    logging.info(f"CHECK ON DEMAND: {PON}")

    record_values = {
        "PON": PON,
        "KPI": KPI,
        "DESCRIPCION": "Test new KPI",
        "DATE": datetime.now(),
    }

    record = LIN_DIAGNOSER(**record_values)

    record.get_oid(kpi=KPI)

    sleep(record.wait)

    rsp = record.get_kpi()

    return rsp


if __name__ == "__main__":
    # uvicorn main:app
    uvicorn.run(app, host=os.getenv("HOST_APP"), port=os.getenv("PORT_APP"))
