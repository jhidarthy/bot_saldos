# scraper.py

# --- Importaciones ---
import pyautogui
import pytesseract
import re
from datetime import datetime
import time
from sqlalchemy import text
from database import SessionLocal, Unidad
from utils_cifrado import descifrar_texto

# --- CONFIGURACIÓN DE CAPTURA ---
LEFT, TOP, WIDTH, HEIGHT = 968, 263, 500, 200

# --- ✅ FUNCIÓN MODIFICADA ---
def extraer_datos(texto_ocr: str) -> dict:
    """
    Extrae datos del texto OCR. Ahora maneja el caso "Saldo expirado".
    Devuelve un diccionario con saldo, vencimiento y un nuevo campo 'detalle'.
    """
    saldo, vencimiento, detalle = None, None, None
    meses = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}

    # Caso 1: Saldo normal y vigente
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

    # Caso 2: Saldo expirado
    match_expirado = re.search(r"Saldo expirado: \$([\d,]+\.\d{2})", texto_ocr)
    if match_expirado:
        # Aunque el saldo está expirado, lo guardamos para tener el dato
        saldo = float(match_expirado.group(1).replace(',', ''))
        vencimiento = None # No hay fecha de vencimiento en este caso
        detalle = "Saldo expirado"

    return {"saldo": saldo, "vencimiento": vencimiento, "detalle": detalle}

# ... (La función procesar_cuenta no necesita cambios, ya que solo llama a extraer_datos) ...
def procesar_cuenta(numero: str, contrasena: str) -> dict or None:
    try:
        print(f"\n--- Procesando número: {numero} ---")
        print("Moviendo al campo de usuario...")
        pyautogui.moveTo(1224, 284, duration=1)
        pyautogui.click()
        pyautogui.PAUSE = 0.5
        print("Limpiando campo de usuario...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        print("Escribiendo número...")
        pyautogui.write(numero, interval=0.1)
        pyautogui.press('tab')
        print("Limpiando campo de contraseña...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        print("Escribiendo contraseña...")
        pyautogui.write(contrasena, interval=0.1)
        print("Haciendo clic en 'Iniciar Sesión'...")
        pyautogui.moveTo(1218, 413, duration=1)
        pyautogui.click()
        print("Esperando a que la página cargue...")
        time.sleep(15)
        texto_extraido = ""
        for intento in range(1, 4):
            print(f"Capturando pantalla (Intento {intento}/3)...")
            screenshot = pyautogui.screenshot(region=(LEFT, TOP, WIDTH, HEIGHT))
            texto_extraido = pytesseract.image_to_string(screenshot, lang='spa')
            if "Saldo Amigo" in texto_extraido or "Saldo expirado" in texto_extraido: # <--- Pequeña mejora aquí
                print("¡Captura de datos exitosa!")
                break
            else:
                print("La captura no contiene la información esperada. Reintentando...")
                time.sleep(5)
                if intento == 3:
                    print("Se superó el número de reintentos.")
        print("Cerrando sesión...")
        pyautogui.moveTo(1433, 114, duration=1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(1409, 316, duration=1)
        pyautogui.click()
        time.sleep(5) 
        return extraer_datos(texto_extraido)
    except Exception as e:
        print(f"❌ Ocurrió un error crítico durante la automatización para {numero}: {e}")
        return None

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("El script comenzará en 5 segundos...")
    time.sleep(5)
    db = SessionLocal()
    try:
        unidades = db.execute(text("SELECT unidad, numero_celular, contrasena FROM unidades_login")).fetchall()
        print("se da clic en el area de trabajo y F5 para recargar pagina")
        pyautogui.moveTo(1234, 17, duration=1)
        pyautogui.click()
        time.sleep(2)
        pyautogui.moveTo(469, 100, duration=1)
        pyautogui.click()
        time.sleep(9)
        for unidad_info in unidades:
            try:
                contrasena = descifrar_texto(unidad_info.contrasena)
            except Exception:
                print(f"❌ Error al descifrar contraseña para {unidad_info.numero_celular}. Saltando...")
                continue

            datos_obtenidos = procesar_cuenta(unidad_info.numero_celular, contrasena)
            
            registro = Unidad(
                unidad=unidad_info.unidad,
                numero_celular=unidad_info.numero_celular,
                fecha_consulta=datetime.now(),
                cliente_administrador_id=1
            )

            # ✅ LÓGICA DE GUARDADO MODIFICADA
            if datos_obtenidos and datos_obtenidos.get("saldo") is not None:
                print(f"✅ Éxito para {unidad_info.numero_celular}. Detalle: {datos_obtenidos['detalle']}. Guardando en BD...")
                registro.saldo = datos_obtenidos["saldo"]
                registro.fecha_vencimiento = datos_obtenidos["vencimiento"]
                registro.estado_consulta = "Exitoso"
                registro.detalle = datos_obtenidos["detalle"] # Guardamos el detalle
            else:
                print(f"❌ Fallo para {unidad_info.numero_celular}. Registrando en BD.")
                registro.estado_consulta = "Fallido"
                registro.detalle = "Error de OCR o página no cargada" # Un detalle para el fallo

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