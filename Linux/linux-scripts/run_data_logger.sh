#!/bin/bash
echo "=========================================="
echo "Ubicacion actual: $PWD"
echo "=========================================="

# 1. Ruta para llegar al venv (Subir 2 niveles y entrar en scripts/linux)
# Asumiendo estructura original: ../../scripts/linux/venv/bin/activate
VENV_PATH="../../scripts/linux/venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    echo "[INFO] Activando entorno virtual..."
    source "$VENV_PATH"
else
    echo "[ERROR] No encuentro el venv en: $VENV_PATH"
    echo "[INFO] Intentando usar conda tfg_opensim..."
    source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
    conda activate tfg_opensim 2>/dev/null
fi

# 2. Ejecutar el script (Subir 1 nivel y entrar en examples)
SCRIPT_PATH="../examples/data_logger.py"

if [ -f "$SCRIPT_PATH" ]; then
    echo "[INFO] Ejecutando data_logger.py..."
    python3 "$SCRIPT_PATH"
else
    echo "[ERROR] No encuentro el archivo en: $SCRIPT_PATH"
fi