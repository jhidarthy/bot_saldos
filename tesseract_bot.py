# scraper.py

# --- Importaciones de librerías estándar ---
import pyautogui
import pytesseract
from PIL import Image
import time
import re
from datetime import datetime

# --- Importaciones de la Base de Datos y Cifrado ---
from sqlalchemy import text
from database import SessionLocal, Unidad # <-- 1. CAMBIO AQUÍ: Importamos 'Unidad' en lugar de 'Saldo'
from utils_cifrado import descifrar_texto


def extraer_datos(texto_ocr: str) -> dict:
    # ... (Sin cambios aquí)
    saldo = None
    vencimiento = None
    meses = { 'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12 }
    match_saldo = re.search(r"Saldo Amigo: \$([\d,]+\.\d{2})", texto_ocr)
    if match_saldo:
        saldo_texto = match_saldo.group(1).replace(',', '')
        saldo = float(saldo_texto)
    match_fecha = re.search(r"Vencimiento: (\d{1,2}) de (\w+) del (\d{4})", texto_ocr, re.IGNORECASE)
    if match_fecha:
        dia, mes_nombre, anio = match_fecha.groups()
        mes_numero = meses.get(mes_nombre.lower())
        if mes_numero:
            vencimiento = datetime(int(anio), mes_numero, int(dia)).date()
    return {"saldo": saldo, "vencimiento": vencimiento}

def procesar_cuenta(numero: str, contrasena: str) -> dict or None:
    # ... (Sin cambios aquí)
    try:
        print(f"\n--- Procesando número: {numero} ---")
        print("Moviendo al campo de usuario...")
        pyautogui.moveTo(1224, 284, duration=1)
        pyautogui.click()
        pyautogui.PAUSE = 0.5

       # Limpiar el campo de usuario antes de escribir
        print("Limpiando campo de usuario...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        print("Escribiendo número...")
        pyautogui.write(numero, interval=0.1)
        pyautogui.press('tab')
        
        #  Limpiar el campo de contraseña antes de escribir
        print("Limpiando campo de contraseña...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        pyautogui.write(contrasena, interval=0.1)
        print("Haciendo clic en 'Iniciar Sesión'...")
        pyautogui.moveTo(1218, 413, duration=1)
        pyautogui.click()
        print("Esperando a que la página cargue...")
        time.sleep(16)
        texto_extraido = ""
        for intento in range(1, 4):
            print(f"Capturando pantalla (Intento {intento}/3)...")
            screenshot = pyautogui.screenshot(region=(968, 263, 500, 200)) # Coordenadas directamente aquí
            texto_extraido = pytesseract.image_to_string(screenshot, lang='spa')
            if "Saldo Amigo" in texto_extraido and "Vencimiento" in texto_extraido:
                print("¡Captura de datos exitosa!")
                break
            else:
                print("La captura no contiene la información esperada. Reintentando en 5 segundos...")
                time.sleep(5)
                if intento == 3:
                    print("Se superó el número de reintentos. La información no pudo ser leída.")
        print("Cerrando sesión...")
        pyautogui.moveTo(1433, 114, duration=1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(1409, 316, duration=1)
        pyautogui.click()
        time.sleep(8) 
        return extraer_datos(texto_extraido)
    except Exception as e:
        print(f"❌ Ocurrió un error crítico durante la automatización para {numero}: {e}")
        return None


# --- EJECUCIÓN PRINCIPAL DEL SCRIPT ---
if __name__ == "__main__":
    print("El script comenzará en 5 segundos...")
    time.sleep(5)
    
    db = SessionLocal()
    
    try:
        print("Obteniendo lista de unidades desde la base de datos...")
        unidades_a_procesar = db.execute(
            text("SELECT unidad, numero_celular, contrasena FROM unidades_login")
        ).fetchall()
        
        for unidad_info in unidades_a_procesar:
            try:
                contrasena_real = descifrar_texto(unidad_info.contrasena)
            except Exception:
                print(f"❌ Error: No se pudo descifrar la contraseña para {unidad_info.numero_celular}. Saltando...")
                continue

            datos_obtenidos = procesar_cuenta(unidad_info.numero_celular, contrasena_real)
            
            # --- 2.  Creamos un objeto 'Unidad' ---
            registro = Unidad(
                unidad=unidad_info.unidad,
                numero_celular=unidad_info.numero_celular,
                fecha_consulta=datetime.now(),
                cliente_administrador_id=1
            )

            if datos_obtenidos and datos_obtenidos.get("saldo") is not None:
                print(f"✅ Éxito para {unidad_info.numero_celular}. Guardando en BD...")
                registro.saldo = datos_obtenidos["saldo"]
                registro.fecha_vencimiento = datos_obtenidos["vencimiento"]
                registro.estado_consulta = "Exitoso"
            else:
                print(f"❌ Fallo para {unidad_info.numero_celular}. Registrando en BD.")
                registro.estado_consulta = "Fallido"

            db.add(registro)
            db.commit()

    except Exception as e:
        print(f"❌ Error crítico en el proceso principal: {e}")
        db.rollback()
    finally:
        db.close()
        print("\n" + "="*50)
        print("✅ PROCESO DE SCRAPING COMPLETADO.")
        print("="*50)