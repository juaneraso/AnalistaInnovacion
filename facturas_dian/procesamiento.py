
import os

import pandas as pd
from pypdf import PdfReader

from .extraccion import (
    extraer_productos,
    extraer_productos_formato_alternativo,
    limpiar_descripcion,
    obtener_valor,
)


# ============================================================
# PROCESAMIENTO DE UNA FACTURA
# ============================================================

def procesar_factura(ruta_pdf, carpeta_csv, nit_password):

    nombre_archivo = os.path.basename(ruta_pdf)

    print("\n" + "=" * 80)
    print("ARCHIVO:", nombre_archivo)

    reader = PdfReader(ruta_pdf)

    # Desbloquear PDF si está protegido
    if reader.is_encrypted:

        resultado = reader.decrypt(nit_password)

        if not resultado:
            raise ValueError(
                "No se pudo desbloquear el PDF con el NIT indicado."
            )

    # Extraer texto de todas las páginas
    texto = ""

    for pagina in reader.pages:
        texto += (pagina.extract_text() or "") + "\n"

    if not texto.strip():
        raise ValueError("El PDF no contiene texto extraíble.")

    # Extraer datos generales
    numero_factura = obtener_valor(
        texto,
        ["Número de Factura", "Numero de Factura"]
    )

    fecha = obtener_valor(
        texto,
        ["Fecha de Emisión", "Fecha de Emision"]
    )

    nit_emisor = obtener_valor(
        texto,
        ["Nit del Emisor", "NIT del Emisor"]
    )

    print("Factura:", numero_factura)
    print("Fecha:", fecha)
    print("NIT emisor:", nit_emisor)

    # Primer intento: estructura principal
    productos = extraer_productos(texto)

    # Segundo intento: estructura alternativa
    if not productos:

        print("Probando formato alternativo...")

        productos = extraer_productos_formato_alternativo(texto)

    if not productos:
        raise ValueError(
            "No se pudo extraer ningún producto."
        )

    # Construir registros
    registros = []

    for producto in productos:

        registros.append({
            "numero_factura": numero_factura,
            "fecha": fecha,
            "nit_emisor": nit_emisor,
            "codigo": producto["codigo"],
            "descripcion": limpiar_descripcion(
                producto["descripcion"]
            ),
            "cantidad": producto["cantidad"],
            "precio_unitario": producto["precio_unitario"]
        })

    df = pd.DataFrame(registros)

    # Crear nombre del CSV
    nombre_sin_extension = os.path.splitext(
        nombre_archivo
    )[0]

    ruta_salida = os.path.join(
        carpeta_csv,
        nombre_sin_extension + ".csv"
    )

    # Guardar CSV
    df.to_csv(
        ruta_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("Productos encontrados:", len(df))
    print("CSV generado:", ruta_salida)

    return len(df)


# ============================================================
# PROCESAMIENTO DE TODOS LOS PDF
# ============================================================

def procesar_pdfs(carpeta_pdf, carpeta_csv, nit_password):

    os.makedirs(carpeta_csv, exist_ok=True)

    archivos = [
        archivo
        for archivo in os.listdir(carpeta_pdf)
        if archivo.lower().endswith(".pdf")
    ]

    total = len(archivos)
    procesados = 0
    fallidos = 0

    print("\nFACTURAS ENCONTRADAS:", total)

    for archivo in archivos:

        ruta_pdf = os.path.join(
            carpeta_pdf,
            archivo
        )

        try:

            cantidad = procesar_factura(ruta_pdf, carpeta_csv, nit_password)

            procesados += 1

        except Exception as error:

            fallidos += 1

            print("ERROR:", error)

    # Resumen final
    print("\n")
    print("=" * 80)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 80)

    print("Total de PDF:", total)
    print("Procesados correctamente:", procesados)
    print("Fallidos:", fallidos)

    if total:
        porcentaje = (procesados / total) * 100
        print(f"Porcentaje de éxito: {porcentaje:.2f}%")

    print("\nCSV guardados en:", carpeta_csv)

    return procesados, fallidos
