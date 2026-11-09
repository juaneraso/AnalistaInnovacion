import argparse

from facturas_dian import config


def crear_parser():
    parser = argparse.ArgumentParser(
        description="Descarga facturas electrónicas de la DIAN y extrae sus productos a CSV."
    )
    parser.add_argument(
        "accion",
        nargs="?",
        choices=["todo", "descargar", "procesar"],
        default="todo",
        help="Qué ejecutar (por defecto: todo).",
    )
    parser.add_argument(
        "--facturas",
        default=config.ARCHIVO_FACTURAS,
        help=f"JSON con la lista de facturas (por defecto: {config.ARCHIVO_FACTURAS}).",
    )
    parser.add_argument(
        "--descargas",
        default=config.CARPETA_DESCARGAS,
        help="Carpeta donde se guardan/leen los PDF.",
    )
    parser.add_argument(
        "--password",
        default=None,
        help=f"NIT del adquiriente (contraseña de los PDF). También se puede usar {config.VARIABLE_PASSWORD}.",
    )
    return parser


def main():
    args = crear_parser().parse_args()

    carpeta_pdf = args.descargas
    carpeta_csv = f"{carpeta_pdf}/csv"

    if args.accion in ("todo", "descargar"):
      
        from facturas_dian.descarga import descargar_facturas

        facturas = config.cargar_facturas(args.facturas)
        descargar_facturas(facturas, carpeta_pdf)

    if args.accion in ("todo", "procesar"):
        from facturas_dian.procesamiento import procesar_pdfs

        password = config.obtener_password(args.password)
        procesar_pdfs(carpeta_pdf, carpeta_csv, password)


if __name__ == "__main__":
    main()
