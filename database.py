import sys
import datetime
import urllib.parse
from contextlib import contextmanager

# Importaciones de SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, DECIMAL, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# ==========================================
# 1. CONFIGURACIÓN DE LA CONEXIÓN
# ==========================================

# Tus credenciales confirmadas
DB_USER = "bot_user"
DB_PASS_RAW = "pswd_Saldos2025"  # Tu contraseña real
DB_HOST = "10.21.0.3"            # Tu IP Privada de Cloud SQL
DB_NAME = "bot_saldos_db"

# PASO CRÍTICO: Codificar la contraseña para evitar errores con caracteres especiales
# .strip() elimina posibles espacios en blanco invisibles al copiar/pegar
DB_PASS_ENCODED = urllib.parse.quote_plus(DB_PASS_RAW.strip())

# USAMOS EL DRIVER 'mysql-connector-python' 
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS_ENCODED}@{DB_HOST}/{DB_NAME}"

# Configuración del Engine optimizada para instancia e2-micro (1GB RAM)
engine = create_engine(
    DATABASE_URL,
    pool_recycle=1800,  # Reciclar conexiones cada 30 min (Google las cierra a los 60 min)
    pool_pre_ping=True, # Verificar si la conexión sigue viva antes de usarla (Vital)
    pool_size=5,        # Mantener solo 5 conexiones abiertas para ahorrar RAM
    max_overflow=10     # Permitir picos temporales de hasta 15 conexiones
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# ==========================================
# 2. DEFINICIÓN DE MODELOS (TABLAS)
# ==========================================

class ClienteAdministrador(Base):
    __tablename__ = "cliente_administrador"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    
    # Relación bidireccional
    unidades = relationship("Unidad", back_populates="cliente_admin")


class Unidad(Base):
    __tablename__ = "unidad"
    
    id = Column(Integer, primary_key=True, index=True)
    unidad = Column(String(100), nullable=False)
    numero_celular = Column(String(20), nullable=False, index=True)
    saldo = Column(DECIMAL(10, 2), default=0.00)
    fecha_vencimiento = Column(Date)
    fecha_consulta = Column(DateTime, default=datetime.datetime.utcnow)
    estado_consulta = Column(String(50))
    detalle = Column(String(255), nullable=True) 
    
    # Llave foránea
    cliente_administrador_id = Column(Integer, ForeignKey("cliente_administrador.id"))
    cliente_admin = relationship("ClienteAdministrador", back_populates="unidades")


class UnidadLogin(Base):
    __tablename__ = "unidades_login"
    
    id = Column(Integer, primary_key=True)
    unidad = Column(String(100), nullable=False, unique=True)
    numero_celular = Column(String(20), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False, index=True)

# ==========================================
# 3. UTILIDAD DE SESIÓN SEGURA
# ==========================================

@contextmanager
def get_db_session():
    """
    Context manager para manejar sesiones de base de datos de forma segura.
    Asegura que la sesión se cierre siempre, incluso si hay errores.
    
    Uso:
        with get_db_session() as db:
            db.query(Unidad).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit() # Opcional: Auto-commit si todo sale bien
    except Exception as e:
        session.rollback() # Deshacer cambios si hubo error
        raise e
    finally:
        session.close() # Siempre cerrar la conexión

# ==========================================
# 4. BLOQUE PRINCIPAL (TEST DE CONEXIÓN)
# ==========================================

if __name__ == "__main__":
    print(f"--- INICIANDO SISTEMA BOT ---")
    print(f"Conectando a {DB_HOST} usando mysql-connector...")
    
    try:
        # Crea las tablas si no existen
        Base.metadata.create_all(bind=engine)
        print("✅ CONEXIÓN EXITOSA: Tablas verificadas.")
        
        # Prueba de consulta simple
        with get_db_session() as db:
            num_unidades = db.query(Unidad).count()
            print(f"ℹ️  Unidades registradas en DB: {num_unidades}")
            
    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN:")
        print(f"{e}")
