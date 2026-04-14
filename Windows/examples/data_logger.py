import os
import sys
import time
import csv
import signal
import bota_driver
from datetime import datetime
from collections import deque

# ==========================================
# 1. SETUP DE SEGURIDAD (Apagado Seguro)
# ==========================================
stop_flag = False

def signal_handler(signum, frame):
    """Atrapa el Ctrl+C para apagar el sensor de forma segura antes de salir"""
    global stop_flag
    print("\n[INFO] Ctrl+C pressed. Stopping sensor gracefully...")
    stop_flag = True

signal.signal(signal.SIGINT, signal_handler)
# ==========================================
# 2. RUTAS DE CARPETAS Y ARCHIVOS
# ==========================================
# Ruta para guardar el CSV
data_folder = r"C:\Users\alexs\Desktop\bota_driver_py_example\SensONE-T80\data"
os.makedirs(data_folder, exist_ok=True)

# Nombre de archivo con fecha y hora para no sobrescribir
from datetime import datetime
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = os.path.join(data_folder, f"force_data_{timestamp_str}.csv")

# --- RUTA DEL JSON ACTUALIZADA ---
# 1. Obtenemos la carpeta donde está este script (SensONE-T80/examples)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Subimos un nivel (a SensONE-T80) y entramos en la carpeta 'driver'
config_path = os.path.join(os.path.dirname(current_dir), "driver", "bota_binary_gen0.json")

# ==========================================
# 3. LÓGICA PRINCIPAL (DRIVER + CSV + DISPLAY)
# ==========================================
print("="*50)
print("SENS-ONE T80 DATA LOGGER & MONITOR")
print(f"Archivo de datos: {file_path}")
print("Presiona Ctrl + C para detener la grabación.")
print("="*50 + "\n")

try:
    # --- A. INICIALIZAR EL HARDWARE ---
    bota_ft_sensor_driver = bota_driver.BotaDriver(config_path)
    print(f" >>>>>>>>>>> BotaDriver version: {bota_ft_sensor_driver.get_driver_version_string()} <<<<<<<<<<<< ")

    if not bota_ft_sensor_driver.configure():
        raise RuntimeError("Error al configurar el driver")

    print("[INFO] Haciendo TARA... No toque el sensor.")
    time.sleep(1)
    if not bota_ft_sensor_driver.tare():
        raise RuntimeError("Error al hacer la tara")

    if not bota_ft_sensor_driver.activate():
        raise RuntimeError("Error al activar el driver")
    
    print("[INFO] Sensor ACTIVO. Grabando y monitoreando...\n")

    # --- B. CONFIGURACIÓN DE PANTALLA ---
    PRINTING_FREQUENCY = 1.0  # Hz (Se actualiza la info en pantalla cada 1 seg)
    max_samples = 100
    reading_times = deque(maxlen=max_samples)
    last_reading_time = time.perf_counter()

    # --- C. BUCLE DE GRABACIÓN Y LECTURA ---
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Cabecera del CSV (puedes añadir más columnas si quieres guardar todo)
        writer.writerow(['Time_s', 'Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])
        
        start_time = time.perf_counter()
        last_print_time = start_time

        while not stop_flag:
            # 1. Leer frame del sensor
            bota_frame = bota_ft_sensor_driver.read_frame_blocking()
            
            # 2. Cálculo de tiempos y frecuencia
            current_reading_time = time.perf_counter()
            reading_duration = current_reading_time - last_reading_time
            last_reading_time = current_reading_time
            reading_times.append(reading_duration)
            
            elapsed_time = round(current_reading_time - start_time, 4)
            
            # 3. Extraer datos del frame
            f = bota_frame.force
            t = bota_frame.torque
            s = bota_frame.status

            # 4. Guardar en CSV (Guardamos las 3 fuerzas y 3 torques)
            writer.writerow([elapsed_time, f[0], f[1], f[2], t[0], t[1], t[2]])

            # 5. Imprimir en pantalla (Monitoreo visual)
            if current_reading_time - last_print_time >= 1.0/PRINTING_FREQUENCY:
                # Calcular frecuencia real de actualización
                avg_freq = len(reading_times) / sum(reading_times) if reading_times else 0

                print("----------------------------")
                print(f"TIEMPO: {elapsed_time} s")
                print(f"Status: [throttled={s.throttled}, overrange={s.overrange}, invalid={s.invalid}]")
                print(f"Force  (N) : [{f[0]:.2f}, {f[1]:.2f}, {f[2]:.2f}]")
                print(f"Torque (Nm): [{t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f}]")
                print(f"Temp: {bota_frame.temperature:.1f} °C  |  Timestamp: {bota_frame.timestamp}")
                print(f"Update Rate: {avg_freq:.2f} Hz")
                print("----------------------------")
                last_print_time = current_reading_time

except Exception as e:
    print(f"\n[ERROR FATAL]: {e}")
    
finally:
    print("\n" + "="*50)
    print("Cerrando hardware de forma segura...")
    if 'bota_ft_sensor_driver' in locals():
        bota_ft_sensor_driver.deactivate()
        bota_ft_sensor_driver.shutdown()
        
    print(f"Grabación finalizada. Datos en: {file_path}")
    print("="*50)
    sys.exit(0)