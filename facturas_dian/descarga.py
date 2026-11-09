import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Parche para silenciar el error de cierre de undetected-chromedriver en Windows
uc.Chrome.__del__ = lambda self: None


def descargar_facturas(lista_facturas, ruta_descargas):
    """Descarga cada factura de la lista, con reintentos por factura."""

    ruta_descargas = os.path.abspath(ruta_descargas)
    os.makedirs(ruta_descargas, exist_ok=True)

    # Recorrer cada factura de la lista una por una
    for index, factura in enumerate(lista_facturas, start=1):
        cufe_actual = factura["cufe"]
        nit_actual = factura["nit"]

        print(f"\n========================================")
        print(f"📄 Procesando factura {index} de {len(lista_facturas)}")
        print(f"========================================")

        max_intentos = 3
        intento_actual = 0
        proceso_exitoso = False

        # Bucle de reintentos para CADA factura individual
        while intento_actual < max_intentos and not proceso_exitoso:
            intento_actual += 1
            print(f"\n🔄 [Intento {intento_actual} de {max_intentos}] Abriendo navegador...")

            # Opciones de Chrome para la carpeta de descargas
            options = uc.ChromeOptions()
            prefs = {
                "download.default_directory": ruta_descargas,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            options.add_experimental_option("prefs", prefs)

            driver = uc.Chrome(options=options)
            wait = WebDriverWait(driver, 15)

            try:
                driver.get("https://catalogo-vpfe.dian.gov.co/User/SearchDocument")
                driver.maximize_window()
                driver.execute_script("window.scrollTo(0, 400);")

                print("\n👉 Realiza la verificación en el navegador si aparece el captcha inicial.")
                time.sleep(30)

                print("\nIngresando datos de la consulta...")

                # 1. Rellenar el código CUFE
                input_cufe = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//input[@placeholder='Ingrese el código CUFE or UUID' or @placeholder='Ingrese el código CUFE o UUID']",
                    ))
                )
                input_cufe.clear()
                input_cufe.send_keys(cufe_actual)

                # 2. Rellenar el NIT del emisor
                input_nit = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//input[contains(@placeholder, 'NIT') or contains(@placeholder, 'nit')]",
                    ))
                )
                input_nit.clear()
                input_nit.send_keys(nit_actual)

                # 3. Hacer clic en el botón Buscar
                btn_buscar = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[normalize-space()='Buscar']")
                    )
                )
                btn_buscar.click()
                print("✅ Formulario enviado. Esperando a que carguen los resultados...")
                time.sleep(12)

                # -------------------------------------------------------------
                # VALIDACIÓN 1: Verificar que llegamos a la página de resultados
                # -------------------------------------------------------------
                try:
                    wait_resultados = WebDriverWait(driver, 10)
                    wait_resultados.until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Factura electrónica')]"))
                    )
                    print("✅ Seguridad pasada: Texto 'Factura electrónica' detectado en pantalla.")

                except Exception:
                    print("⚠️ No se pudo llegar a la página con el texto 'Factura electrónica'.")
                    driver.quit()

                    if intento_actual < max_intentos:
                        print("🛑 Cerrando navegador, esperando 5 segundos para reintentar desde el inicio...")
                        time.sleep(5)
                        continue
                    else:
                        print(f"❌ Se agotaron los intentos para la factura {index} (Error en Página 1).")
                        break

                # Clic en el enlace de descarga del PDF
                print("Buscando el enlace de descarga del PDF...")
                link_descargar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='downloadLink' and contains(., 'Descargar PDF')]"))
                )
                link_descargar.click()
                print("🎉 ¡Clic en 'Descargar PDF' realizado con éxito!")

                # Manejo del modal de advertencia final y clic en "Aceptar"
                print("Esperando el modal de confirmación de contraseña...")
                time.sleep(5)
                btn_aceptar_modal = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-content']//button[@data-bb-handler='del' and normalize-space()='Aceptar']"))
                )
                btn_aceptar_modal.click()

                # -------------------------------------------------------------
                # VALIDACIÓN 2: Detectar el falso positivo (Error de seguridad tras aceptar)
                # -------------------------------------------------------------
                print("Verificando si la descarga fue real o saltó bloqueo de seguridad...")
                time.sleep(15)  # Breve pausa para dar tiempo a que aparezca el modal de error si se bloqueó

                bloqueo_post_descarga = False
                try:                    
                    aviso_seguridad = driver.find_elements(By.XPATH, "//div[@class='modal-content']//*[contains(normalize-space(text()), 'El campo de seguridad no está completo')]")
                    if len(aviso_seguridad) > 0 and aviso_seguridad[0].is_displayed():
                        bloqueo_post_descarga = True
                except:
                    pass

                if bloqueo_post_descarga:
                    print("⚠️ [Falso Positivo Detectado] Salió: 'El campo de seguridad no está completo' tras hacer clic en Aceptar.")
                    driver.quit()

                    if intento_actual < max_intentos:
                        print("🛑 Cerrando navegador, esperando 5 segundos para reintentar esta factura...")
                        time.sleep(5)
                        continue
                    else:
                        print(f"❌ Se agotaron los intentos para la factura {index} por bloqueo de seguridad final.")
                        break

                # 🌟 ÉXITO REAL
                print(f"\n✅ **¡Factura {index} descargada con éxito!** (Guardada en: {ruta_descargas})")
                proceso_exitoso = True

                # Pausa breve para asegurar que el archivo baje antes de cerrar
                time.sleep(4)
                driver.quit()

            except Exception as e:
                print(f"❌ Ocurrió un error inesperado en este intento: {e}")
                try:
                    driver.quit()
                except:
                    pass

                if intento_actual < max_intentos:
                    print("🔄 Esperando 5 segundos para reintentar esta factura...")
                    time.sleep(5)
                else:
                    print(f"❌ Se agotaron los intentos máximos para la factura {index}.")

    print(f"\n🏁 ¡Proceso masivo finalizado! Revisa tu carpeta '{os.path.basename(ruta_descargas)}'.")
