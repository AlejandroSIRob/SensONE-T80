import os
import sys
import time
import csv
import signal
import bota_driver
from datetime import datetime

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
# 3. LÓGICA PRINCIPAL (DRIVER + CSV)
# ==========================================
print("="*50)
print("Starting SensONE-T80 Data Logger")
print(f"Logging data to: {file_path}")
print("Press Ctrl + C to stop recording.")
print("="*50 + "\n")

try:
    # --- A. INICIALIZAR EL HARDWARE ---
    bota_ft_sensor_driver = bota_driver.BotaDriver(config_path)
    
    if not bota_ft_sensor_driver.configure():
        raise RuntimeError("Failed to configure driver")

    print("[INFO] Taring sensor (Setting to zero)... Please do not touch it.")
    time.sleep(1) # Pequeña pausa para asegurar que nadie lo toca
    if not bota_ft_sensor_driver.tare():
        raise RuntimeError("Failed to tare sensor")

    if not bota_ft_sensor_driver.activate():
        raise RuntimeError("Failed to activate driver")
    
    print("[INFO] Sensor ACTIVE. Starting data logging...\n")

    # --- B. GRABACIÓN EN CSV ---
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        # Opcional: Si OpenSim necesita Fx y Fy, puedes añadirlos aquí
        writer.writerow(['Time_s', 'Fz_Newtons'])
        
        start_time = time.perf_counter()
        last_print_time = start_time
        
        # Bucle de lectura (se detiene si pulsas Ctrl+C)
        while not stop_flag:
            
            # 1. Leer el bloque de datos real (Se queda esperando hasta que llega el dato)
            bota_frame = bota_ft_sensor_driver.read_frame_blocking()
            current_time = round(time.perf_counter() - start_time, 4)
            
            # 2. Extraer la Fuerza Z
            # Nota: bota_frame.force es una lista [Fx, Fy, Fz]. El índice 2 es la Z.
            force_z = round(bota_frame.force[2], 3)
            
            # 3. Guardar en el Excel
            writer.writerow([current_time, force_z])
            
            # 4. Imprimir en pantalla solo 2 veces por segundo (0.5s) para no saturar la consola
            if time.perf_counter() - last_print_time >= 0.5:
                print(f"Logging -> Time: {current_time} s  |  Fz: {force_z} N")
                last_print_time = time.perf_counter()

# --- C. APAGADO SEGURO (Se ejecuta siempre, haya error o no) ---
except Exception as e:
    print(f"\n[FATAL ERROR]: {e}")
    
finally:
    print("\n" + "="*50)
    print("Shutting down hardware safely...")
    
    # Intenta desactivar y apagar el driver si existe
    if 'bota_ft_sensor_driver' in locals():
        bota_ft_sensor_driver.deactivate()
        bota_ft_sensor_driver.shutdown()
        
    print(f"Recording successfully finished!")
    print(f"Your data is safe in: {file_path}")
    print("="*50)
    sys.exit(0)