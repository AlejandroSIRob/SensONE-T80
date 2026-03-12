import time
import csv
import os

# 1. Definimos la ruta absoluta exacta para la carpeta data
data_folder = r"C:\Users\alexs\Desktop\bota_driver_py_example\SensONE-T80\data"
file_name = "force_data.csv"

# 2. Crea la carpeta "data" en esa ruta exacta si no existe
os.makedirs(data_folder, exist_ok=True)

# 3. Combina la ruta de la carpeta con el nombre del archivo
file_path = os.path.join(data_folder, file_name)

print("="*50)
print(f"Starting SensONE-T80 SENSOR")
print(f"Logging data to: {file_path}")
print("Press Ctrl + C in this console to stop recording.")
print("="*50 + "\n")

# ====================================================================
# ⚠️ IMPORTANTE PARA CUANDO TENGAS EL CABLE:
# Aquí arriba tendrás que pegar las 2 o 3 líneas del ejemplo original 
# de Bota Systems que sirven para conectar el sensor al puerto COM.
# (Algo del estilo: sensor = BotaDriver("COM3") o similar).
# ====================================================================

# Abrimos el CSV en modo escritura ('w')
with open(file_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Escribimos la cabecera (nombres de las columnas)
    writer.writerow(['Time_s', 'Fz_Newtons'])
    
    # Guardamos el momento exacto de inicio
    start_time = time.time()
    
    try:
        # Bucle infinito de grabación
        while True:
            # Calculamos el tiempo transcurrido (redondeado a 3 decimales)
            current_time = round(time.time() - start_time, 3)
            
            # ----------------------------------------------------
            # LECTURA REAL DEL SENSOR
            # ----------------------------------------------------
            # Leemos la fuerza Z real del hardware
            raw_force_z = sensor.read().forces.z
            
            # La redondeamos a 2 decimales para no tener números infinitos en el Excel
            force_z = round(raw_force_z, 2) 
            
            # Guardamos la fila en el CSV
            writer.writerow([current_time, force_z])
            
            # Imprimimos en pantalla para ver que todo fluye
            print(f"Logging -> Time: {current_time} s  |  Fz: {force_z} N")
            
            # Pausa de 0.1 segundos (Graba a 10 Hz)
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        # Salida segura al pulsar Ctrl+C
        print("\n" + "="*50)
        print(f"Recording successfully finished!")
        print(f"Your data is safe in the folder: {file_path}")
        print("="*50)