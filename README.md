# SensONE T80 - Data Logger

Este repositorio contiene el script en Python para leer en tiempo real los datos del sensor de fuerza y par **SensONE T80** (Bota Systems) y exportarlos a un archivo `.csv`. Ideal para sincronizar fuerzas con captura de movimiento (Xsens) o análisis en OpenSim.

## ⚙️ Instalación y Requisitos

1. **Clonar los drivers oficiales:**
   Debes clonar el repositorio base de Bota Systems en tu ordenador:
   ```bash
   git clone [https://gitlab.com/botasys/drivers/bota_driver_py_example](https://gitlab.com/botasys/drivers/bota_driver_py_example)
   ```

2. **Ubicar el proyecto:**
   Copia esta carpeta (`SensONE-T80`) y pégala **dentro** de la carpeta `bota_driver_py_example` que acabas de descargar.

3. **Instalar dependencias (Requiere Python 3.12+):**
   Abre la terminal en la carpeta principal del driver, activa tu entorno virtual y ejecuta:
   ```bash
   pip install .
   ```

## 🚀 Uso

1. Conecta el sensor SensONE T80 al puerto USB de tu equipo.
2. Abre una terminal dentro de esta carpeta (`SensONE-T80`).
3. Ejecuta el script de grabación:
   ```bash
   python data_logger.py
   ```
*Nota: Para detener la grabación y guardar el archivo de forma segura, pulsa `Ctrl + C` en la consola.*

## 📊 Formato de Salida

El script generará (o sobrescribirá) el archivo `force_data.csv` en esta misma carpeta con la siguiente estructura:

| Time_s | Fz_Newtons |
|--------|------------|
| 0.100  | 12.34      |
| 0.200  | 15.60      |
| ...    | ...        |