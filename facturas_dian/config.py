"""Configuración general y carga de la lista de facturas."""

import json
import os

# Carpeta donde se guardan los PDF descargados
CARPETA_DESCARGAS = os.path.abspath("descargas_facturas")

# Carpeta de salida de los CSV
CARPETA_CSV = os.path.join(CARPETA_DESCARGAS, "csv")

# Archivo por defecto con la lista de facturas a descargar
ARCHIVO_FACTURAS = "facturas.json"

# Variable de entorno con el NIT del adquiriente (contraseña de los PDF)
VARIABLE_PASSWORD = "NIT_PASSWORD"


def cargar_facturas(ruta_json):
    """
    Lee el archivo JSON con la lista de facturas.

    Formato esperado:
        [{"cufe": "...", "nit": "..."}, ...]
    """
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(
            f"No se encontró '{ruta_json}'. "
            "Copia 'facturas.example.json' a 'facturas.json' y completa tus datos."
        )

    with open(ruta_json, encoding="utf-8") as archivo:
        facturas = json.load(archivo)

    for i, factura in enumerate(facturas, start=1):
        if "cufe" not in factura or "nit" not in factura:
            raise ValueError(f"La factura #{i} debe tener los campos 'cufe' y 'nit'.")

    return facturas


def obtener_password(argumento=None):
    """Devuelve el NIT usado como contraseña (argumento o variable de entorno)."""
    password = argumento or os.environ.get(VARIABLE_PASSWORD)

    if not password:
        raise ValueError(
            "Falta el NIT del adquiriente. Usa --password o define "
            f"la variable de entorno {VARIABLE_PASSWORD}."
        )

    return password
