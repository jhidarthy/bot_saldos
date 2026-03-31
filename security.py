# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# --- Configuración de Seguridad ---

# 1. Esquema de seguridad: Le dice a FastAPI que lea el token de la cabecera "Authorization"
#    tokenUrl="token" le dice a la documentación de Swagger que debe ir al endpoint /token para autenticarse.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 2. Configuración de Hashing de contraseñas
#    Usamos bcrypt, que es el estándar de la industria.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Configuración de Tokens JWT
#    ? ¡IMPORTANTE! Cambia esta llave secreta. Puedes generar una con:
#    # python -c 'import secrets; print(secrets.token_hex(32))'
SECRET_KEY = "tu_llave_secreta_super_segura_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Duración del token

# --- Funciones de Contraseña ---

def verify_password(plain_password, hashed_password):
    """Verifica que una contraseña plana coincida con un hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash de una contraseña plana."""
    return pwd_context.hash(password)

# --- Funciones de Token JWT ---

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crea un nuevo token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Lógica de Autenticación de Usuario ---

# Para este ejemplo, usaremos un usuario "hardcodeado".
# En un sistema real, buscarías este usuario en tu base de datos.
FAKE_USER_DB = {
    "admin": {
        "username": "admin",
        # Esta es la contraseña "admin123" hasheada
        "hashed_password": get_password_hash("admin123"), 
        "full_name": "Administrador Principal",
    }
}

def authenticate_user(username: str, password: str):
    """
    Comprueba si un usuario existe y si la contraseña es correcta.
    """
    user = FAKE_USER_DB.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# --- La Dependencia "Guardia de Seguridad" ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Esta es la función "guardia". Se ejecuta en cada endpoint protegido.
    Lee el token, lo decodifica y devuelve los datos del usuario.
    Si el token es inválido, lanza un error HTTP 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Obtiene el usuario de nuestra "base de datos"
    user = FAKE_USER_DB.get(username)
    if user is None:
        raise credentials_exception
    
    # Devuelve el usuario, que puede ser usado en el endpoint si se necesita
    return user