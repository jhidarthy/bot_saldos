@echo off

REM --- Configura tus rutas aqui ---
REM Ruta al directorio del entorno virtual (un nivel arriba)
SET "VENV_DIR=C:\Users\jjc\Documents\Proyectos\venvBot"

REM Ruta a tu script de Python (en el directorio actual)
SET "PYTHON_SCRIPT=C:\Users\jjc\Documents\Proyectos\API_Saldos\tesseract_bot_v1.py"


REM --- Activacion y ejecucion ---
echo [INFO] Activando entorno virtual desde %VENV_DIR%...
CALL %VENV_DIR%\Scripts\activate.bat

echo [INFO] Entorno activado. Ejecutando %PYTHON_SCRIPT%...
python %PYTHON_SCRIPT%

echo [INFO] Proceso terminado.
pause