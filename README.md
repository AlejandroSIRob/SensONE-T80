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
   pip install pandas numpy matplotlib scipy
   ```
4. **Modificar Rutas de archivos:**
   Modificar vuestras rutas en los siguientes archivos:
   * `examples/data_logger.py`
   * `driver/bota_binary_gen0.json`
   * `windows-scripts/run_data_logger.bat`
   * `sync-imu/sync.py`

## 📂 Estructura del Proyecto

* `examples/data_logger.py`: Script principal de adquisición y monitoreo en tiempo real.
* `sync-imu/sync.py`: Script de fusión multimodal (Sincroniza IMU + Fuerza basándose en impactos).
* `driver/bota_binary_gen0.json`: Configuración del puerto COM y parámetros del hardware.
* `windows-scripts/run_data_logger.bat`: Lanzador automatizado para Windows.
* `data/` y `sync-imu/sinc-data/`: Carpetas donde se almacenan las grabaciones y los datasets fusionados.

## 🚀 1.-Uso

1. Conecta el sensor SensONE T80 al puerto USB de tu equipo.
2. Abre una terminal dentro de esta carpeta (`SensONE-T80`).
3. Ejecuta el script de grabación:
   ```bash
   .\windows-scripts\run_data_logger.bat
   ```

* **Puesta a cero**: El script realiza una **tara automática** (software tare) al inicio. No toques el sensor durante el primer segundo tras la activación.
* **Monitoreo**: La consola mostrará en tiempo real la fuerza (N), el torque (Nm), la temperatura y la frecuencia de actualización (Hz).
* **Finalización**: Pulsa `Ctrl + C` para cerrar el sensor de forma segura y finalizar la escritura del archivo.


## 🔄 2.-Uso

Para alinear temporalmente una toma de fuerza con una toma de captura de movimiento (buscando automáticamente un patrón de 3 impactos), ejecuta desde la carpeta principal `SensONE-T80`:

```bash
python sync-imu/sync.py --imu "ruta/a/cinematica.sto" --force "ruta/a/force_data.csv"
```
El script generará un DATASET_MAESTRO.csv remuestreado a 100 Hz exactos, junto con gráficas de validación en la carpeta sync-imu/sinc-data/.

## 📊 Datos de Salida

Los archivos se guardan en la carpeta `/data` con el formato `force_data_YYYYMMDD_HHMMSS.csv`.

| Time_s | Fx | Fy | Fz | Tx | Ty | Tz |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.0001 | ... | ... | ... | ... | ... | ... |

* **Unidades**: Fuerzas en Newtons (N), Torques en Newton-metro (Nm).
* **Frecuencia**: Los datos se registran a la frecuencia máxima permitida por el bus serie (~400 Hz).