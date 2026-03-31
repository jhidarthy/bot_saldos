# database.py
from sqlalchemy import (create_engine, Column, Integer, String, Float, 
                        DateTime, Date, DECIMAL, ForeignKey)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
# Reemplaza con tus credenciales.
DATABASE_URL = "mysql+pymysql://admin:root_saldos_pass@127.0.0.1/saldos_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELO PARA LA TABLA 'cliente_administrador' ---
class ClienteAdministrador(Base):
    __tablename__ = "cliente_administrador"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    
    # La relación ahora se llama 'unidades' para mayor claridad
    unidades = relationship("Unidad", back_populates="cliente_admin")

# --- MODELO CORREGIDO PARA LA TABLA 'unidad' ---
class Unidad(Base):
    __tablename__ = "unidad"

    id = Column(Integer, primary_key=True, index=True)
    unidad = Column(String(100), nullable=False)
    numero_celular = Column(String(20), nullable=False, index=True)
    saldo = Column(DECIMAL(10, 2), default=0.00)
    fecha_vencimiento = Column(Date)
    fecha_consulta = Column(DateTime, default=datetime.datetime.utcnow)
    estado_consulta = Column(String(50))

    detalle = Column(String(255), nullable=True) # Para guardar notas como "Saldo expirado"
    
    cliente_administrador_id = Column(Integer, ForeignKey("cliente_administrador.id"))
    
    # La relación inversa apunta a ClienteAdministrador
    cliente_admin = relationship("ClienteAdministrador", back_populates="unidades")

# --- MODELO PARA LA TABLA 'unidades_login' ---
class UnidadLogin(Base):
    __tablename__ = "unidades_login"
    
    id = Column(Integer, primary_key=True)
    unidad = Column(String(100), nullable=False, unique=True)
    numero_celular = Column(String(20), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)


# Función para crear todas las tablas si no existen
if __name__ == "__main__":
    print("Creando tablas en la base de datos (si no existen)...")
    Base.metadata.create_all(bind=engine)
    print("¡Proceso completado!")