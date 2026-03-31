# utils_cifrado.py
from cryptography.fernet import Fernet

# --- 1. GENERA TU LLAVE SECRETA UNA SOLA VEZ ---
# Ejecuta este bloque una vez desde tu terminal (`python utils_cifrado.py`)
# y guarda la llave que se imprime en un lugar seguro.
def generar_llave():
    llave = Fernet.generate_key()
    print(f"Tu llave secreta es: {llave.decode()}")
    print("¡Guárdala en un lugar seguro! Por ejemplo, una variable de entorno.")

# --- 2. FUNCIONES DE CIFRADO Y DESCIFRADO ---
# Pega aquí la llave que generaste.
LLAVE_SECRETA = b'lPGS9LgewgGoXmfedNth-VvNGzwXrQC9aFzRhKjtnng='
cipher_suite = Fernet(LLAVE_SECRETA)

def cifrar_texto(texto_plano: str) -> str:
    """Cifra un texto y devuelve el resultado como string."""
    texto_bytes = texto_plano.encode('utf-8')
    texto_cifrado_bytes = cipher_suite.encrypt(texto_bytes)
    return texto_cifrado_bytes.decode('utf-8')

def descifrar_texto(texto_cifrado: str) -> str:
    """Descifra un texto y devuelve el texto plano."""
    texto_cifrado_bytes = texto_cifrado.encode('utf-8')
    texto_plano_bytes = cipher_suite.decrypt(texto_cifrado_bytes)
    return texto_plano_bytes.decode('utf-8')

if __name__ == '__main__':
    # --- EJEMPLO DE USO ---
    # generar_llave() # Descomenta esta línea para generar una nueva llave
    
    contrasena_original = "Test3264"
    contrasena_cifrada = cifrar_texto(contrasena_original)
    contrasena_descifrada = descifrar_texto(contrasena_cifrada)
    
    print(f"Original: {contrasena_original}")
    print(f"Cifrada (esto es lo que guardas en la BD): {contrasena_cifrada}")
    print(f"Descifrada (lo que usa el scraper): {contrasena_descifrada}")