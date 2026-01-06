from machine import UART, Pin, DAC
import time

# Initialize UART1 with GPIO4 TX, GPIO5 RX, baudrate 115200
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
dac = DAC(Pin(25))  # DAC output pin (GPIO25)
led = Pin(2, Pin.OUT)  # Onboard LED for data indication

print("UART1 DAC output started")

while True:
    if uart.any():
        data = uart.read(1)
        if data:
            val = data[0]
            dac.write(val)  # Output analog voltage
            led.toggle()    # Toggle LED on data received
    else:
        time.sleep_ms(1)
