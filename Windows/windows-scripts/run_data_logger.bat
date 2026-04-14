@echo off
echo ==========================================
echo Ubicacion actual: %cd%
echo ==========================================

:: 1. Ruta para llegar al venv (Subir 2 niveles y entrar en scripts\windows)
set VENV_PATH=..\..\scripts\windows\venv\Scripts\activate

if exist "%VENV_PATH%.bat" (
    echo [INFO] Activando entorno virtual...
    call %VENV_PATH%
) else (
    echo [ERROR] No encuentro el venv en: %VENV_PATH%
)

:: 2. Ejecutar el script (Subir 1 nivel y entrar en examples)
set SCRIPT_PATH=..\examples\data_logger.py

if exist "%SCRIPT_PATH%" (
    echo [INFO] Ejecutando data_logger.py...
    python %SCRIPT_PATH%
) else (
    echo [ERROR] No encuentro el archivo en: %SCRIPT_PATH%
)

pause