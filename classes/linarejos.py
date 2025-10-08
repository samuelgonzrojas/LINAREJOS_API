# linarejos.py

import logging
import requests

# import urllib3
import json, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración básica para que se muestre INFO y superiores
logging.basicConfig(level=logging.INFO)


class API_LINAREJOS:
    def __init__(self, **kwargs):
        self.HOST = os.getenv("HOST_LINAREJOS")
        self.IP = os.getenv("IP_LINAREJOS")
        self.PROTOCOL = os.getenv("PROTOCOL_LINAREJOS")
        self.PORT = int(os.getenv("PORT_LINAREJOS"))
        self.USERNAME = os.getenv("USERNAME_LINAREJOS")
        self.PASSWORD = os.getenv("PASSWORD_LINAREJOS")
        self.URL = f"{self.PROTOCOL}://{self.HOST}:{self.PORT}/apilinarejos"
        self.wait = 35


class LIN_DIAGNOSER(API_LINAREJOS):
    def __init__(self, **kwargs):
        super().__init__()
        self.PON = kwargs.get("PON")
        self.OLT, self.SLOT, self.PORT = self.PON.split("-")
        self.OID = kwargs.get("OID", None)
        self.KPI = kwargs.get("KPI", "KPI#1#5")
        self.KPI_RESPONSE = json.loads(kwargs.get("KPI_RESPONSE", "{}") or "{}")
        self.retries = kwargs.get("retries", 0)
        self.DATE = datetime.now()
        self.OID_date = None
        self.KPI_date = None

        # inicializa la cabecera de las peticiones a Linarejos
        self.session = requests.Session()
        self.session.auth = (self.USERNAME, self.PASSWORD)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_oid(self, **kwargs):
        logging.info(f"OID - REQ - {self.PON}")
        oid_form = {
            "operacion": "exec",
            "usuario": self.USERNAME,
            "kpi": self.KPI,
            "olt": self.OLT,
            "slot": self.SLOT,
            "port": self.PORT,
        }

        if all(oid_form):
            json_data = json.dumps(oid_form).encode("utf-8")
            self.headers["Content-Length"] = f"{len(json_data)}"

            try:
                rsp = self.session.post(
                    self.URL,
                    data=json_data,
                    headers=self.headers,
                    verify=False,
                    timeout=(2, 5),
                )
                status_code = rsp.status_code

            except Exception as e:
                logging.error(f"OID - ER_1 - {self.PON} - {str(e)}")

            # si rsp es OK, devuelve el OID
            if status_code == 200:
                rsp_json = rsp.json()
                if "oid" in rsp_json.keys():
                    self.OID = str(rsp_json["oid"])
                    self.KPI_date = datetime.now() + timedelta(seconds=self.wait)
                    logging.info(f"OID - OK_1 - {self.PON}")
                else:
                    logging.error(f"OID - ER_2 - {self.PON}")
            else:
                logging.error(f"OID - ER_3 - {self.PON}")

    def get_kpi(self):
        logging.info(f"KPI - REQ - {self.PON}")
        kpi_form = {"operacion": "result", "oid": self.OID}
        json_data = json.dumps(kpi_form).encode("utf-8")
        try:
            rsp = self.session.post(
                self.URL,
                data=json_data,
                headers=self.headers,
                timeout=(2, 5),
                verify=False,
            )
            status_code = rsp.status_code
        except Exception as e:
            logging.error(f"KPI - ER_1 - {self.PON} - {str(e)}")

        self.KPI_date = datetime.now()

        if status_code == 200:
            rsp_json = rsp.json()

            # Si la operación ha devuelto lectura de KPI, aparece como "resultado"
            if "resultado" in rsp_json.keys():
                self.KPI_RESPONSE = rsp_json.get("resultado")
                logging.info(f"KPI - OK_1 - {self.PON}")
                return self.KPI_RESPONSE
            # Si hubo algún error, aparece como "result"
            elif "result" in rsp_json.keys():
                self.STATUS = rsp_json.get("result")
                logging.error(f"KPI - ER_2 - {self.PON} - {self.STATUS}")

        else:
            logging.error(f"KPI - ER_3 {self.PON}: {self.STATUS}")
