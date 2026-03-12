"""
FUSION MULTIMODAL CIENTÍFICA (IMU + FORCE)
-------------------------------------------------------------
Autor: Alejandro Solar Iglesias
Descripción:
  - Sincronización de cinemática (Xsens IMU) y cinética (Bota SensONE Fuerza).
  - Todo sincronizado al 3º impacto detectado en el eje Z (Fz).
  - Exportación fija a: C:\...\SensONE-T80\sync-imu\sinc-data
Para ejecutar: 
  - python Sync.py --ruta_toma "ruta/a/la/toma"
  - python Sync.py --imu .\cinematica.sto --force .\force_data.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
import os
import glob
import argparse

# --- CONFIGURACIÓN ---
FS_MASTER = 100.0           # Frecuencia a la que se exportará el CSV final
FS_FORCE = 400.0            # Frecuencia aprox de grabación del SensONE
WINDOW_SEARCH = [2.0, 60.0] # Ventana de tiempo donde buscar los impactos
CLUSTER_MAX_DURATION = 2.5  # Tiempo máximo entre el 1º y el 3º impacto (segundos)
MIN_PEAK_DIST_S = 0.15      # Tiempo mínimo de separación entre impactos

# =========================================================
# 1. PROCESAMIENTO IMU Y FUERZA
# =========================================================
def procesar_imu_acc(df, col_name):
    """Calcula el Jerk (derivada de la aceleración) para el IMU"""
    try:
        val = df[col_name].values
        if df[col_name].dtype == object:
            val = df[col_name].str.split(',', expand=True)[0].astype(float).values
        vel = np.diff(val, prepend=val[0])
        acc = np.diff(vel, prepend=vel[0])
        return np.abs(acc)
    except:
        return np.zeros(len(df))

def procesar_xsens_mano(df):
    t = df['time'].values
    # Busca la columna que contenga la palabra 'hand' o 'mano'
    col_hand = next((c for c in df.columns if 'hand' in c.lower() or 'mano' in c.lower()), None)
    if not col_hand: return np.zeros(len(t)), t
    return procesar_imu_acc(df, col_hand), t

def procesar_force(df):
    t = df['Time_s'].values
    # Dependiendo de cómo lo hayas guardado, busca Fz
    col_fz = next((c for c in df.columns if 'Fz' in c), None)
    fz = df[col_fz].values if col_fz else np.zeros(len(t))
    return np.abs(fz), t

# =========================================================
# 2. MOTOR DE DETECCIÓN (Sincronización)
# =========================================================
def detectar_tercer_impacto(senal, tiempo, nombre_sensor, fs, verbose=True):
    senal = np.nan_to_num(senal)
    offset = np.mean(senal[:int(fs)]) # Tara dinámica
    senal_clean = np.abs(senal - offset)
    mx = np.max(senal_clean)
    if mx == 0: return None
    senal_norm = senal_clean / mx

    # Barrido de sensibilidad para encontrar el patrón de 3 impactos
    for sensibilidad in [0.4, 0.25, 0.1, 0.05]:
        peaks, _ = find_peaks(senal_norm, height=sensibilidad, distance=int(MIN_PEAK_DIST_S * fs))
        if len(peaks) >= 3:
            for i in range(len(peaks) - 2):
                t1 = tiempo[peaks[i]]
                t3 = tiempo[peaks[i+2]]
                if (t3 - t1) < CLUSTER_MAX_DURATION:
                    if verbose: print(f"   [{nombre_sensor}] Patrón detectado (Sensibilidad {sensibilidad}). T(3º) = {t3:.3f}s")
                    return t3

    # Fallback si no encuentra patrón de 3
    idx_max = np.argmax(senal_norm)
    t_max = tiempo[idx_max]
    if verbose: print(f"   [{nombre_sensor}] WARNING: Patrón no claro. Usando Máximo Absoluto: {t_max:.3f}s")
    return t_max

# =========================================================
# 3. GENERACIÓN DE REPORTES GRÁFICOS
# =========================================================
def generar_reporte_imu(df, imu_cols, folder):
    n = len(imu_cols)
    if n == 0: return
    fig, axes = plt.subplots(n, 1, figsize=(12, 3 + 2*n), sharex=True)
    if n == 1: axes = [axes]
    for i, col in enumerate(imu_cols):
        ax = axes[i]
        nombre = col.replace('_imu', '').replace('_', ' ').title()
        ax.plot(df['Time'], df[col], '#2980b9', lw=1.2)
        ax.set_title(f"IMU: {nombre}", loc='left', fontweight='bold', fontsize=9, color='#154360')
        ax.set_ylabel("Acc", fontsize=8)
        ax.grid(True, alpha=0.3); ax.axvline(0, color='r', ls='--', alpha=0.6)
    axes[-1].set_xlabel("Tiempo (s)"); plt.tight_layout()
    plt.savefig(os.path.join(folder, "REPORTE_IMU.png"), dpi=100); plt.close()

def generar_reporte_force(df, folder):
    force_cols = [c for c in df.columns if 'FORCE_' in c]
    if not force_cols: return
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Gráfica de Fuerzas
    if 'FORCE_Fx' in df.columns: axes[0].plot(df['Time'], df['FORCE_Fx'], label='Fx', alpha=0.8)
    if 'FORCE_Fy' in df.columns: axes[0].plot(df['Time'], df['FORCE_Fy'], label='Fy', alpha=0.8)
    if 'FORCE_Fz' in df.columns: axes[0].plot(df['Time'], df['FORCE_Fz'], label='Fz (Impacto)', color='red', lw=1.5)
    axes[0].set_title("SensONE - Fuerzas (N)", loc='left', fontweight='bold')
    axes[0].set_ylabel("Newtons"); axes[0].legend(); axes[0].grid(True, alpha=0.3)
    axes[0].axvline(0, color='k', ls='--', alpha=0.6)

    # Gráfica de Torques
    if 'FORCE_Tx' in df.columns: axes[1].plot(df['Time'], df['FORCE_Tx'], label='Tx', alpha=0.8)
    if 'FORCE_Ty' in df.columns: axes[1].plot(df['Time'], df['FORCE_Ty'], label='Ty', alpha=0.8)
    if 'FORCE_Tz' in df.columns: axes[1].plot(df['Time'], df['FORCE_Tz'], label='Tz', alpha=0.8)
    axes[1].set_title("SensONE - Torques (Nm)", loc='left', fontweight='bold')
    axes[1].set_ylabel("Nm"); axes[1].set_xlabel("Tiempo (s)"); axes[1].legend(); axes[1].grid(True, alpha=0.3)
    axes[1].axvline(0, color='k', ls='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(os.path.join(folder, "REPORTE_FORCE.png"), dpi=100); plt.close()

# =========================================================
# 4. MAIN
# =========================================================
def main():
    parser = argparse.ArgumentParser(description='Sync IMU (Xsens) and FORCE (SensONE)')
    parser.add_argument('ruta_toma', nargs='?', default=None, help='Carpeta con subcarpetas PROCESADO-Xsens y FORCE')
    parser.add_argument('--imu', help='Ruta directa al fichero IMU (.sto)')
    parser.add_argument('--force', help='Ruta directa al fichero Fuerza SensONE (.csv)')
    args = parser.parse_args()

    # Resolver rutas de entrada
    if args.imu and args.force:
        k_path, f_path = args.imu, args.force
        ruta_toma = os.path.dirname(k_path) or '.'
    else:
        if not args.ruta_toma:
            parser.print_help(); return
        ruta_toma = args.ruta_toma
        try:
            k_path = glob.glob(os.path.join(ruta_toma, "PROCESADO-Xsens", "*.sto"))[0]
            f_path = glob.glob(os.path.join(ruta_toma, "FORCE", "*.csv"))[0]
        except IndexError:
            print("[ERROR] Faltan archivos XSens (.sto) o FORCE (.csv) en las subcarpetas de la toma.")
            return

    print(f"\nANÁLISIS V7 (IMU + FORCE): {os.path.basename(ruta_toma)}\n")

    # 1. LECTURA DE DATOS
    df_k = pd.read_csv(k_path, sep='\t', skiprows=5)
    t_k = df_k['time'].values
    sig_k, _ = procesar_xsens_mano(df_k)

    df_f = pd.read_csv(f_path)
    sig_f, t_f = procesar_force(df_f)

    # 2. SINCRONIZACIÓN (Buscar el 3º golpe)
    mask_k = (t_k > WINDOW_SEARCH[0]) & (t_k < WINDOW_SEARCH[1])
    t_sync_k = detectar_tercer_impacto(sig_k[mask_k], t_k[mask_k], "XSENS", 60.0)
    
    mask_f = (t_f > WINDOW_SEARCH[0]) & (t_f < WINDOW_SEARCH[1])
    t_sync_f = detectar_tercer_impacto(sig_f[mask_f], t_f[mask_f], "FORCE_Z", FS_FORCE)

    # Prioridad de metrónomo temporal: La Fuerza es más precisa
    if t_sync_f is not None:
        t_sync_ref = t_sync_f
        print("-> Referencia temporal maestra: SENSOR DE FUERZA (SensONE)")
    else:
        t_sync_ref = t_sync_k
        print("-> Referencia temporal maestra: XSENS")

    if t_sync_ref is None:
        print("[ERROR] No se pudo detectar ningún impacto para sincronizar.")
        return

    # 3. FUSIÓN AL DATASET MAESTRO (100 Hz)
    t_fin = max(t_f[-1], t_k[-1]) - t_sync_ref
    t_master = np.arange(-3.0, t_fin, 1/FS_MASTER) # Empieza 3s antes del golpe
    df_out = pd.DataFrame({'Time': t_master})
    
    # Función de interpolación
    remap = lambda t, y, t0: interp1d(t - t0, y, bounds_error=False, fill_value=0)(t_master)

    # Añadir columnas de IMU
    for col in [c for c in df_k.columns if 'imu' in c]:
        df_out[col] = remap(t_k, procesar_imu_acc(df_k, col), t_sync_k if t_sync_k else t_sync_ref)

    # Añadir columnas de FUERZA
    columnas_fuerza = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']
    for col in columnas_fuerza:
        actual_col = next((c for c in df_f.columns if col in c), None)
        if actual_col:
            df_out[f'FORCE_{col}'] = remap(t_f, df_f[actual_col].values, t_sync_f if t_sync_f else t_sync_ref)

    # =========================================================
    # 4. GUARDAR EN RUTA FIJA
    # =========================================================
    out_folder = r"C:\Users\alexs\Desktop\bota_driver_py_example\SensONE-T80\sync-imu\sync-data"
    os.makedirs(out_folder, exist_ok=True)
    
    # Añadir el nombre de la toma al archivo para no sobrescribir si procesas varias
    nombre_toma = os.path.basename(os.path.normpath(ruta_toma))
    if nombre_toma in ['.', '']: nombre_toma = "manual_sync"
    
    out_file = os.path.join(out_folder, f"DATASET_MAESTRO_{nombre_toma}.csv")
    df_out.to_csv(out_file, index=False)

    # 5. REPORTES GRÁFICOS
    print("-> Generando gráficas IMU...")
    generar_reporte_imu(df_out, [c for c in df_k.columns if 'imu' in c], out_folder)
    print("-> Generando gráficas FORCE...")
    generar_reporte_force(df_out, out_folder)
    
    print(f"\n[OK] Fusión completada con éxito.")
    print(f" Archivos guardados en: {out_folder}")

if __name__ == "__main__":
    main()