import serial
import time
import csv

SERIAL_PORT = 'COM10'  # Replace with your USB-to-UART adapter COM port
BAUD_RATE = 115200
CSV_FILE = '100_scaled_dac.csv'  # Your single-column scaled DAC CSV file

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud")

    with open(CSV_FILE, 'r') as f:
        reader = csv.reader(f)

        # Uncomment if your CSV has a header row
        # next(reader)  # Skip CSV header

        for row in reader:
            print("Reading row:", row)
            if len(row) < 1:
                print("Skipping row due to insufficient columns")
                continue
            try:
                val = int(row[0])  # Read value from first column
                ser.write(bytes([val]))
                ser.flush()
                print(f"Sent: {val}")
                time.sleep(1/360)  # Delay for ~360 samples/sec (~0.00278 s per sample)
            except Exception as e:
                print("Error sending value:", e)

except Exception as e:
    print("Error:", e)

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
