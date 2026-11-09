# Facturas DIAN

Automatiza dos tareas sobre facturas electrónicas del catálogo de la DIAN (Colombia):

1. **Descarga** los PDF a partir del CUFE y el NIT del emisor (Selenium + `undetected-chromedriver`).
2. **Extrae** los productos de cada PDF (código, descripción, cantidad y precio unitario) y los guarda en un CSV por factura.

## Estructura

```
AnalistaInnovacion/
facturas-dian/
├── main.py                      # CLI (argparse)
├── facturas_dian/
│   ├── config.py                # rutas, carga del JSON de facturas, contraseña
│   ├── descarga.py              # automatización del navegador
│   ├── extraccion.py            # funciones de parseo de texto
│   └── procesamiento.py         # lectura de PDF y generación de CSV
├── facturas.json                # plantilla de la lista de facturas
└── requirements.txt
```

## Requisitos

- Python 3.10 o superior
- Google Chrome instalado
- Windows, Mac o Linux (probado en Windows)

## Instalación

### Windows (PowerShell o CMD)

Ubicate en la ruta

```
cd AnalistaInnovacion/
```

Escribe los siguientes comandos en orden

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En CMD, la activación es `venv\Scripts\activate`.

Si PowerShell bloquea la ejecución de scripts, corre una sola vez:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Vuelve a ejecutar los comandos faltantes

```
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Mac / Linux

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Cuando el entorno virtual esté activo verás `(venv)` al inicio de la línea de la terminal.

## Configuración

1. Las facturas se encuentran en el archivo facturas.json:

   Formato del archivo:

   ```json
   [
     {
       "cufe": "<CUFE de la factura>",
       "nit": "<NIT del emisor>"
     }
   ]
   ```

2. Define el NIT del adquiriente, que es la contraseña de los PDF. Hay dos formas.

   **Opción A: argumento al ejecutar (la más simple)**

   ```
   python main.py --password 900156264
   ```

   **Opción B: variable de entorno** (dura mientras la terminal esté abierta)

   ```
   set NIT_PASSWORD=900156264                    (CMD)
   $env:NIT_PASSWORD="900156264"                 (PowerShell)
   export NIT_PASSWORD=900156264                 (Mac / Linux / Git Bash)
   ```

## Uso

```
python main.py --password 900156264              # descarga y luego procesa
python main.py descargar                         # solo descarga
python main.py procesar --password 900156264     # solo procesa los PDF ya descargados
```

Opciones disponibles:

| Opción        | Descripción                                                                |
| ------------- | -------------------------------------------------------------------------- |
| `--facturas`  | JSON con la lista de facturas (por defecto `facturas.json`)                |
| `--descargas` | Carpeta donde se guardan y leen los PDF (por defecto `descargas_facturas`) |
| `--password`  | NIT del adquiriente, contraseña de los PDF                                 |

Los PDF quedan en `descargas_facturas/` y los CSV en `descargas_facturas/csv/`.

Columnas del CSV: `numero_factura`, `fecha`, `nit_emisor`, `codigo`, `descripcion`, `cantidad`, `precio_unitario`.

## Solución de problemas

**`ModuleNotFoundError: No module named 'distutils'`**
`undetected-chromedriver` usa `distutils`, que se eliminó en Python 3.12. Se resuelve con `pip install setuptools` (ya incluido en `requirements.txt`).

**`cryptography>=3.1 is required for AES algorithm`**
Los PDF de la DIAN están cifrados con AES y `pypdf` necesita `cryptography` para abrirlos. Se resuelve con `pip install cryptography` (ya incluido en `requirements.txt`).

**`Falta el NIT del adquiriente`**
No se entregó la contraseña de los PDF. Usa `--password` o define la variable `NIT_PASSWORD`.

**`No se encontró 'facturas.json'`**
Copia `facturas.example.json` a `facturas.json` y completa los CUFE.

**El comando de activación del entorno virtual no funciona**
Revisa qué terminal usas. En PowerShell o CMD se usa la ruta con `\Scripts\`. En Git Bash o MSYS2 se usa `source venv/Scripts/activate` (con barras normales). Se recomienda usar PowerShell con el Python oficial de Windows.

## Limitaciones

- El sitio de la DIAN muestra un **captcha** que se resuelve manualmente en el navegador. El script espera 30 segundos en cada intento para que lo resuelvas.
- La automatización depende de la estructura HTML actual del sitio. Si cambia, los selectores XPath deben actualizarse.
- La extracción soporta dos formatos de tabla de productos. Las facturas con otro diseño pueden fallar y se reportan en el resumen final.
- Cantidades y precios se guardan como texto, tal como aparecen en el PDF (formato colombiano, por ejemplo `1.500,00`).
- Al procesar se leen todos los PDF de la carpeta de descargas, incluidos los de ejecuciones anteriores.
