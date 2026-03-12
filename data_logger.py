import time
import csv
import random  # We use this to simulate until you get the cable from Saltanat
import os      # NEW: Library to create folders automatically

# 1. Define the folder and file names
data_folder = "data"
file_name = "force_data.csv"

# 2. Create the "data" folder if it doesn't exist yet
os.makedirs(data_folder, exist_ok=True)

# 3. Combine folder and filename (e.g., "data/force_data.csv")
file_path = os.path.join(data_folder, file_name)

print("="*50)
print(f"Starting SensONE-T80 SENSOR")
print(f"Logging data to: {file_path}")
print("Press Ctrl + C in this console to stop recording.")
print("="*50 + "\n")

# Open the CSV file in write mode ('w') using the new path
with open(file_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write the header (column names for Excel/OpenSim)
    writer.writerow(['Time_s', 'Fz_Newtons'])
    
    # Save the exact start time to calculate elapsed time
    start_time = time.time()
    
    try:
        # Infinite logging loop
        while True:
            # Calculate elapsed time in seconds (rounded to 3 decimals)
            current_time = round(time.time() - start_time, 3)
            
            # ----------------------------------------------------
            # READ REAL SENSOR HERE (When you plug in the cable):
            # force_z = sensor.read().forces.z
            # ----------------------------------------------------
            
            # Meanwhile, we generate a simulated force to test the script:
            force_z = round(random.uniform(-2.0, 45.0), 2)
            
            # Save data to the Excel/CSV file (New row)
            writer.writerow([current_time, force_z])
            
            # Print to screen to verify it's working in real-time
            print(f"Logging -> Time: {current_time} s  |  Fz: {force_z} N")
            
            # Pause for 0.1 seconds (Recording at 10 Hz)
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        # Safe exit when pressing Ctrl+C
        print("\n" + "="*50)
        print(f"Recording successfully finished!")
        print(f"Your data is safe in the folder: {file_path}")
        print("="*50)