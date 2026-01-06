ecg-waveform-generator-esp32
================================

This project streams ECG waveforms from a PC to an ESP32 over UART1 and reconstructs them as an analog signal using the ESP32’s internal DAC on GPIO25.  

***

## Overview

- PC sends 8-bit ECG samples (0–255) over a serial link using an external USB-to-UART adapter.  
- ESP32 receives the bytes on UART1 (GPIO5) and writes them directly to the DAC on GPIO25.  
- The analog ECG-like waveform can be visualized on an oscilloscope.  

***

## Hardware Requirements

Reliable waveform reproduction requires the following hardware and a shared ground reference between all devices:

- **ESP32 Dev Board**  
  - Must support an internal DAC.  
  - GPIO25 is used as the DAC output.  

- **USB-to-UART Adapter**  
  - CP210x or similar.  
  - Used to interface the PC with ESP32 UART1.  

- **Oscilloscope**  
  - To view the reconstructed ECG waveform from GPIO25.  

- **Jumper Wires**  
  - For UART, DAC, and ground connections.  
  - Ensure a **common ground** between ESP32, USB-to-UART adapter, and oscilloscope.  

***

## Wiring Configuration

To avoid conflicts with the ESP32’s onboard USB-to-UART (UART0, used for REPL/flashing), the project uses **UART1**.

### UART1 Connections (PC ↔ ESP32)

| USB-to-UART (CP210x) | ESP32 Pin        | Purpose                               |
|----------------------|------------------|---------------------------------------|
| TXD                  | GPIO5 (UART1 RX) | PC to ESP32 data transmission         |
| RXD                  | GPIO4 (UART1 TX) | Optional (not required for one-way TX)|
| GND                  | GND              | Mandatory common ground               |

### DAC Output

- **Signal**: ESP32 GPIO25 → Oscilloscope probe (channel input).  
- **Ground**: ESP32 GND → Oscilloscope ground clip.  

***

## Software Overview

Three main Python scripts handle data preparation, transmission, and reception:

- **`data_save.py`**  
  - Downloads ECG records (e.g., MIT-BIH) from PhysioNet.  
  - Extracts ECG lead samples and scales them to 8-bit integers (0–255).  
  - Outputs a single-column CSV (e.g., `100_scaled_dac.csv`).  

- **`dac-sender.py`** (PC side)  
  - Reads a single-column CSV of scaled ECG samples.  
  - Sends `int(row[0])` as a single byte over serial.  
  - Uses a delay of about `1/360` seconds between samples (~360 samples/sec).  

- **`dac-recieve.py`** (ESP32, MicroPython)  
  - Configures UART1 on GPIO5 (RX) and GPIO4 (TX).  
  - Reads incoming bytes from UART1.  
  - Writes each byte to the DAC (GPIO25) to reconstruct the waveform.  
  - Toggles an LED on GPIO2 for a visual indication on each received sample.  

***

## Getting Started

### 1. Prepare the ESP32

1. Flash **MicroPython** firmware to the ESP32 (using any standard method).  
2. Use an IDE like **Thonny** to:  
   - Connect to the ESP32 via the onboard USB (UART0).  
   - Upload `dac-recieve.py` to the board.  
3. Run `dac-recieve.py`.  
4. The serial console should print:  

   ```text
   UART1 DAC output started
   ```

This indicates that UART1 is initialized and the DAC output loop is running.

***

### 2. Generate ECG Data (Scaled CSV)

On the PC:

1. Install dependencies:

   ```bash
   pip install requests wfdb pandas numpy
   ```

2. Run the data script:

   ```bash
   python data_save.py
   ```

3. This will generate CSV files such as:

   - `100_scaled_dac.csv`  
   - `101_scaled_dac.csv`  
   - `102_scaled_dac.csv`  

Each generated file:

- Is **single-column**.  
- Contains **integers from 0 to 255**, suitable as 8-bit DAC input values.  

If you provide your own CSV, ensure the same format:

- Exactly **one column**.  
- **Integer values only**, in the range **0–255**.

***

### 3. Stream the Waveform from the PC

1. Install `pyserial`:

   ```bash
   pip install pyserial
   ```

2. Open `dac-sender.py` and edit:

   - `SERIAL_PORT = 'COM10'`  
     - Replace `'COM10'` with your USB-to-UART adapter’s actual port (e.g., `COM3` on Windows or `/dev/ttyUSB0` on Linux).  
   - `CSV_FILE = '100_scaled_dac.csv'`  
     - Set to the desired scaled ECG CSV file.  

3. Run the sender:

   ```bash
   python dac-sender.py
   ```

4. The PC now streams ECG samples over UART1 at about **360 samples/sec**, and the ESP32 outputs them via DAC on GPIO25.

5. Probe **GPIO25** and **GND** on the oscilloscope to observe the ECG-like waveform.

***

## Troubleshooting

- **No waveform on oscilloscope**  
  - Confirm **common ground** between CP210x, ESP32, and oscilloscope.  
  - Verify wiring:  
    - CP210x TXD → ESP32 GPIO5 (UART1 RX).  
    - ESP32 GPIO25 → oscilloscope channel input.  
  - Check that `dac-recieve.py` is running on the ESP32.  

- **Serial “Access denied” or port busy on PC**  
  - Close any other applications using the same COM port (e.g., Thonny, Arduino Serial Monitor, VS Code serial plugins).  

- **CSV parsing or value errors**  
  - Ensure the CSV has:  
    - No header row (or adjust code accordingly).  
    - A single column.  
    - Only numeric values in the 0–255 range.  

- **Output looks “stepped” or jagged**  
  - This is expected from:  
    - **8-bit DAC resolution** (only 256 discrete levels).  
    - **360 samples/sec** replay rate.    

***

## License

This project is released under the **MIT License**.  