import re

# ============================================================
# DATOS GENERALES DE LA FACTURA
# ============================================================

def obtener_valor(texto, etiquetas):
    """
    Busca una etiqueta en el texto y obtiene su valor,
    ya sea en la misma línea o en la siguiente.
    """

    lineas = [
        linea.strip()
        for linea in texto.splitlines()
    ]

    for i, linea in enumerate(lineas):

        for etiqueta in etiquetas:

            patron = re.compile(
                r"^" + re.escape(etiqueta) + r"\s*:?\s*(.*)$",
                re.IGNORECASE
            )

            coincidencia = patron.match(linea)

            if coincidencia:

                valor = coincidencia.group(1).strip()

                if valor:
                    return valor

                # Buscar el siguiente contenido no vacío
                for siguiente in lineas[i + 1:]:

                    if siguiente:
                        return siguiente

    return ""


# ============================================================
# PATRONES DE VALIDACIÓN
# ============================================================

PATRON_CANTIDAD = re.compile(r"^\d+,\d{2}$")

PATRON_PRECIO = re.compile(
    r"^\$?\s*[\d.]+,\d{2}$"
)

PATRON_NUMERO_PRODUCTO = re.compile(r"^\d{1,3}$")

PATRON_CODIGO = re.compile(
    r"^[A-Z0-9][A-Z0-9._/-]*$",
    re.IGNORECASE
)


# ============================================================
# MÉTODO PRINCIPAL DE EXTRACCIÓN DE PRODUCTOS
# Formato:
# Número
# Código
# Descripción
# Unidad
# Cantidad
# Precio
# ============================================================

def extraer_productos(texto):

    inicio = re.search(
        r"Detalles?\s+de\s+Productos",
        texto,
        re.IGNORECASE
    )

    if not inicio:
        return []

    seccion = texto[inicio.end():]

    fin = re.search(
        r"Notas Finales|Datos Totales|Hoja\s+\d+\s+de\s+\d+",
        seccion,
        re.IGNORECASE
    )

    if fin:
        seccion = seccion[:fin.start()]

    lineas = [
        linea.strip()
        for linea in seccion.splitlines()
        if linea.strip()
    ]

    productos = []

    i = 0

    while i < len(lineas) - 2:

        # Identificar número de producto
        if PATRON_NUMERO_PRODUCTO.fullmatch(lineas[i]):

            numero = lineas[i]

            # El siguiente elemento debería ser el código
            if i + 1 < len(lineas):

                codigo = lineas[i + 1]

                if PATRON_CODIGO.fullmatch(codigo):

                    # Buscar cantidad seguida de precio
                    for j in range(i + 3, min(i + 20, len(lineas) - 1)):

                        if (
                            PATRON_CANTIDAD.fullmatch(lineas[j])
                            and PATRON_PRECIO.fullmatch(lineas[j + 1])
                        ):

                            # La línea anterior a la cantidad
                            # corresponde normalmente a la unidad.
                            descripcion = " ".join(
                                lineas[i + 2:j - 1]
                            )

                            if descripcion:

                                productos.append({
                                    "codigo": codigo,
                                    "descripcion": descripcion,
                                    "cantidad": lineas[j],
                                    "precio_unitario": lineas[j + 1]
                                })

                                i = j + 2
                                break

                    else:
                        i += 1

                else:
                    i += 1

            else:
                i += 1

        else:
            i += 1

    return productos


# ============================================================
# MÉTODO ALTERNATIVO DE EXTRACCIÓN
# Formato:
# Número
# Descripción
# Código
# Cantidad
# Precio
# ============================================================

def extraer_productos_formato_alternativo(texto):

    inicio = re.search(
        r"Detalles?\s+de\s+Productos",
        texto,
        re.IGNORECASE
    )

    if not inicio:
        return []

    seccion = texto[inicio.end():]

    fin = re.search(
        r"Notas Finales|Datos Totales|Hoja\s+\d+\s+de\s+\d+",
        seccion,
        re.IGNORECASE
    )

    if fin:
        seccion = seccion[:fin.start()]

    lineas = [
        linea.strip()
        for linea in seccion.splitlines()
        if linea.strip()
    ]

    productos = []

    i = 0

    while i < len(lineas):

        if PATRON_NUMERO_PRODUCTO.fullmatch(lineas[i]):

            inicio_producto = i

            # Buscar cantidad seguida de precio
            for j in range(
                i + 2,
                min(i + 20, len(lineas) - 1)
            ):

                if (
                    PATRON_CANTIDAD.fullmatch(lineas[j])
                    and PATRON_PRECIO.fullmatch(lineas[j + 1])
                ):

                    # La línea anterior a cantidad es el código
                    codigo = lineas[j - 1]

                    # Validar que el código tenga formato válido
                    if not PATRON_CODIGO.fullmatch(codigo):
                        continue

                    # La descripción está entre el número
                    # del producto y el código.
                    descripcion = " ".join(
                        lineas[inicio_producto + 1:j - 1]
                    )

                    if descripcion:

                        # Corrección puntual de palabras partidas
                        descripcion = re.sub(
                            r"\bP\s+or\b",
                            "Por",
                            descripcion,
                            flags=re.IGNORECASE
                        )

                        productos.append({
                            "codigo": codigo,
                            "descripcion": descripcion,
                            "cantidad": lineas[j],
                            "precio_unitario": lineas[j + 1]
                        })

                        i = j + 2
                        break

            else:
                i += 1

        else:
            i += 1

    return productos


# ============================================================
# LIMPIEZA DE DESCRIPCIONES
# ============================================================

def limpiar_descripcion(descripcion):

    descripcion = re.sub(
        r"\s+",
        " ",
        descripcion
    ).strip()

    # Aquí agregaremos correcciones específicas
    # cuando revisemos los resultados de los CSV.

    return descripcion
