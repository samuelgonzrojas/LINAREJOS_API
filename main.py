# main.py

import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from routes.api import api

load_dotenv()


# inicialización de app FastAPI
app = FastAPI()
app.include_router(api)


# Ping
@app.get("/ping")
def ping():
    return "OK"


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST_APP", "0.0.0.0"),
        port=int(os.getenv("PORT_APP", 8000)),
    )
