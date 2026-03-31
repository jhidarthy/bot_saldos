# scraper_refactorizado.py

# --- Importaciones ---
import pyautogui
import pytesseract
import re
from datetime import datetime, timedelta
import time
from sqlalchemy import text
from database import SessionLocal, Unidad
from utils_cifrado import descifrar_texto
import os
import random
import subprocess 

# --- CONFIGURACIÓN DE RUTAS UNIVERSALES ---
# Detecta automáticamente /home/nombre_usuario
HOME = os.path.expanduser("~")

# --- CONFIGURACIÓN DE HERRAMIENTAS ---
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
os.environ["DISPLAY"] = ":1"

# --- DEFINICIÓN DE RUTAS DE IMÁGENES (DINÁMICAS) ---
RUTAS_IMAGENES = {
    "usuario": os.path.join(HOME, "imagenes_bot", "campo_usuario.png"),
    "contrasena": os.path.join(HOME, "imagenes_bot", "campo_contrasena.png"),
    "login": os.path.join(HOME, "imagenes_bot", "boton_login.png"),
    "menu_logout": os.path.join(HOME, "imagenes_bot", "boton_menu_logout.png"),
    "confirmar_logout": os.path.join(HOME, "imagenes_bot", "boton_confirmar_logout.png"),
    "foco_pagina": os.path.join(HOME, "imagenes_bot", "area_foco.png"),
}

# --- FUNCIÓN AUXILIAR "INTELIGENTE" ---
def clic_en_imagen(imagen_path: str, reintentos=5, confianza=0.8) -> bool:
    print(f"[CLIC] Buscando '{imagen_path}'...")
    for i in range(reintentos):
        try:
            caja = pyautogui.locateOnScreen(imagen_path, grayscale=True, confidence=confianza)
            if caja:
                punto_central = pyautogui.center(caja)
                print(f"[CLIC] ¡Encontrada! Haciendo clic en {punto_central}")
                pyautogui.moveTo(punto_central, duration=random.uniform(0.2, 0.5))
                pyautogui.click()
                return True
            else:
                if i < (reintentos - 1):
                    print(f"[CLIC] No encontrada. Reintento {i+1}/{reintentos}...")
                    time.sleep(random.uniform(0.8, 1.2)) 
        except Exception as e:
            print(f"[CLIC] Error inesperado buscando {imagen_path}: {e}")
            time.sleep(random.uniform(0.8, 1.2)) 
            
    print(f"[CLIC] ERROR: No se pudo encontrar la imagen '{imagen_path}' después de {reintentos} intentos.")
    return False

# --- CONFIGURACIÓN DE CAPTURA ---
LEFT, TOP, WIDTH, HEIGHT = 650, 271, 531, 206

# --- FUNCIÓN DE EXTRACCIÓN DE DATOS ---
def extraer_datos(texto_ocr: str) -> dict:
    saldo, vencimiento, detalle = None, None, None
    meses = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
    match_normal = re.search(r"Saldo Amigo: \$([\d,]+\.\d{2})", texto_ocr)
    if match_normal:
        saldo = float(match_normal.group(1).replace(',', ''))
        detalle = "Saldo vigente"
        match_fecha = re.search(r"Vencimiento: (\d{1,2}) de (\w+) del (\d{4})", texto_ocr, re.IGNORECASE)
        if match_fecha:
            dia, mes_nombre, anio = match_fecha.groups()
            mes_numero = meses.get(mes_nombre.lower())
            if mes_numero:
                vencimiento = datetime(int(anio), mes_numero, int(dia)).date()
    match_expirado = re.search(r"Saldo expirado: \$([\d,]+\.\d{2})", texto_ocr)
    if match_expirado:
        saldo = float(match_expirado.group(1).replace(',', ''))
        vencimiento = None
        detalle = "Saldo expirado"
    return {"saldo": saldo, "vencimiento": vencimiento, "detalle": detalle}


# --- FUNCIÓN DE PROCESO ---
def procesar_cuenta(numero: str, contrasena: str) -> dict or None:
    datos_extraidos = None 
    try:
        print(f"\n--- Procesando número: {numero} ---")
        
        print("Recargando página (F5) para un estado limpio...")
        pyautogui.press('f5')
        time.sleep(random.uniform(8.0, 10.0)) 

        print("Haciendo clic en campo de usuario...")
        if not clic_en_imagen(RUTAS_IMAGENES["usuario"], reintentos=3):
            print("ERROR: No se encontró el campo de usuario después de recargar. Abortando cuenta.")
            return None 
        
        print("Limpiando campo...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.PAUSE = random.uniform(0.15, 0.3)
        print("Escribiendo número...")
        pyautogui.write(numero, interval=random.uniform(0.08, 0.15))
        pyautogui.press('tab')

        print("Limpiando campo de contraseña...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.PAUSE = random.uniform(0.15, 0.3)
        print("Escribiendo contraseña...")
        pyautogui.write(contrasena, interval=random.uniform(0.08, 0.15))

        print("Haciendo clic en 'Iniciar Sesión'...")
        if not clic_en_imagen(RUTAS_IMAGENES["login"]):
            print("ERROR: No se encontró el botón de login.")
            return None 

        print("Esperando a que la página cargue...")
        time.sleep(random.uniform(14.0, 17.0))

        texto_extraido = ""
        datos_encontrados = False
        for intento in range(1, 4):
            print(f"Capturando pantalla (Intento {intento}/3)...")
            screenshot = pyautogui.screenshot(region=(LEFT, TOP, WIDTH, HEIGHT))
            texto_extraido = pytesseract.image_to_string(screenshot, lang='spa')
            if "Saldo Amigo" in texto_extraido or "Saldo expirado" in texto_extraido:
                print("¡Captura de datos exitosa!")
                datos_encontrados = True
                break
            else:
                print("La captura no contiene la información esperada. Reintentando...")
                time.sleep(random.uniform(4.5, 6.0))
                if intento == 3:
                    print("Se superó el número de reintentos (OCR fallido).")
        
        if datos_encontrados:
            datos_extraidos = extraer_datos(texto_extraido)

    except Exception as e:
        print(f"Ocurrió un error crítico durante la automatización para {numero}: {e}")
    
    finally:
        print("--- Ejecutando proceso de cierre de sesión (limpieza) ---")
        print("Cerrando sesión (Paso 1: Menú)...")
        if not clic_en_imagen(RUTAS_IMAGENES["menu_logout"], reintentos=2):
            print("ADVERTENCIA: No se encontró el botón de menú de logout. (Puede que ya esté deslogueado)")
        else:
            time.sleep(random.uniform(0.8, 1.3))
            print("Cerrando sesión (Paso 2: Confirmar)...")
            if not clic_en_imagen(RUTAS_IMAGENES["confirmar_logout"], reintentos=2):
                print("ADVERTENCIA: No se encontró el botón de confirmar logout.")
        
        print("--- Limpieza finalizada. Continuando... ---")
        time.sleep(random.uniform(3.0, 5.0)) 

    return datos_extraidos 

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("El script comenzará en 5 segundos...")
    time.sleep(random.uniform(4.0, 6.0))
    db = SessionLocal()
    try:
        hoy = datetime.now().date()
        limite_7_dias = hoy + timedelta(days=7)
        # Solo seleccionamos las cuentas ACTIVAS
        unidades_login_info = db.execute(text("SELECT unidad, numero_celular, contrasena FROM unidades_login WHERE activo = TRUE")).fetchall()
        print(f"Se encontraron {len(unidades_login_info)} cuentas totales. Verificando cuáles procesar...")

        cuentas_a_procesar = []
        
        print("Filtrando cuentas según los criterios...")
        for u in unidades_login_info:
            ultimo_registro = db.query(Unidad).filter(
                Unidad.numero_celular == u.numero_celular
            ).order_by(
                Unidad.fecha_consulta.desc()
            ).first()

            procesar = False
            
            if not ultimo_registro:
                print(f"[FILTRO] {u.numero_celular}: Nueva. Marcada para procesar.")
                procesar = True
            else:
                if ultimo_registro.estado_consulta == "Exitoso" and ultimo_registro.fecha_consulta.date() == hoy:
                    print(f"[FILTRO] {u.numero_celular}: OK. Ya se consultó con éxito hoy. Omitiendo.")
                else:
                    if ultimo_registro.estado_consulta == "Fallido":
                        print(f"[FILTRO] {u.numero_celular}: Último estado 'Fallido'. Marcada para procesar.")
                        procesar = True
                    elif ultimo_registro.saldo is not None and ultimo_registro.saldo < 100:
                        print(f"[FILTRO] {u.numero_celular}: Saldo bajo ({ultimo_registro.saldo}). Marcada para procesar.")
                        procesar = True
                    elif ultimo_registro.fecha_vencimiento is not None:
                        if ultimo_registro.fecha_vencimiento <= limite_7_dias:
                            print(f"[FILTRO] {u.numero_celular}: Vence pronto o está vencida ({ultimo_registro.fecha_vencimiento}). Marcada para procesar.")
                            procesar = True
                        else:
                             print(f"[FILTRO] {u.numero_celular}: OK (Vigente). Omitiendo.")
                    else:
                        print(f"[FILTRO] {u.numero_celular}: Registro existente pero sin datos claros. Marcada para procesar.")
                        procesar = True

            if procesar:
                cuentas_a_procesar.append(u)

        print(f"\nSe procesarán {len(cuentas_a_procesar)} de {len(unidades_login_info)} cuentas.")

        if len(cuentas_a_procesar) == 0:
            print("No hay cuentas que procesar hoy. Saliendo.")
            db.close()
            exit()
            
        # --- APERTURA INICIAL DEL NAVEGADOR ---
        print("Abriendo Firefox en la URL de login...")
        subprocess.Popen(["firefox", "https://www.mitelcel.com/mitelcel/login"])
        time.sleep(12) 

        print("Dando clic en el área de trabajo (foco)...")
        clic_en_imagen(RUTAS_IMAGENES["foco_pagina"]) 
        time.sleep(random.uniform(1.5, 2.5))
        
        total_unidades = len(cuentas_a_procesar)
        for i, unidad_info in enumerate(cuentas_a_procesar):
            
            # --- LÓGICA DE REINICIO DE MEMORIA (CADA 20 CUENTAS) ---
            if i > 0 and i % 20 == 0:
                print("\n" + "!"*40)
                print(f"LIMPIEZA DE MEMORIA: Han pasado 20 cuentas. Reiniciando Firefox...")
                print("!"*40 + "\n")
                os.system("pkill -f firefox")
                time.sleep(5) 
                print("Abriendo Firefox limpio...")
                subprocess.Popen(["firefox", "https://www.mitelcel.com/mitelcel/login"])
                time.sleep(12) 
                print("Recuperando foco...")
                clic_en_imagen(RUTAS_IMAGENES["foco_pagina"])
                time.sleep(3)
            # -------------------------------------------------------

            print("\n" + "="*20 + f" CUENTA {i+1}/{total_unidades} " + "="*20)
            try:
                contrasena = descifrar_texto(unidad_info.contrasena)
            except Exception as e:
                print(f"Error al descifrar contraseña para {unidad_info.numero_celular}:{e}. Intentando con Default...")
                contrasena = "DETFU2020" #continue

            datos_obtenidos = procesar_cuenta(unidad_info.numero_celular, contrasena)
            
            registro = Unidad(
                unidad=unidad_info.unidad,
                numero_celular=unidad_info.numero_celular,
                fecha_consulta=datetime.now(),
                cliente_administrador_id=1
            )

            if datos_obtenidos and datos_obtenidos.get("saldo") is not None:
                print(f"Éxito para {unidad_info.numero_celular}. Detalle: {datos_obtenidos['detalle']}. Guardando en BD...")
                registro.saldo = datos_obtenidos["saldo"]
                registro.fecha_vencimiento = datos_obtenidos["vencimiento"]
                registro.estado_consulta = "Exitoso"
                registro.detalle = datos_obtenidos["detalle"]
            else:
                print(f"Fallo para {unidad_info.numero_celular}. Registrando en BD.")
                registro.estado_consulta = "Fallido"
                registro.detalle = "Error de OCR o página no cargada"

            db.add(registro)
            db.commit()

            if i < total_unidades - 1:
                espera = random.uniform(35.0, 50.0)
                print(f"--- Pausa humana: Esperando {espera:.1f} segundos antes de la siguiente cuenta ---")
                time.sleep(espera)

    except Exception as e:
        print(f"Error crítico en el proceso principal: {e}")
        db.rollback()
    
    finally:
        # --- ¡LIMPIEZA FINAL DE RECURSOS! ---
        print("\n" + "*"*50)
        print("SCRIPT TERMINADO (O ERROR). CERRANDO FIREFOX PARA LIBERAR MEMORIA.")
        print("*"*50)
        os.system("pkill -f firefox")
        
        db.close()
        print("PROCESO DE SCRAPING COMPLETADO.")
