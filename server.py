import socket
import serial

# Adjust COM port (the one connected to COMPIM)
SERIAL_PORT = "COM4"
BAUD = 9600

ser = serial.Serial("COM4", BAUD)
print("[SERVER] Serial COM open:", "COM4")

# TCP Server
HOST = "127.0.0.1"
PORT = 6000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("[SERVER] Waiting for AI commands...")

while True:
    conn, addr = s.accept()
    data = conn.recv(1024).decode().strip()
    print("[RECEIVED FROM AI]:", data)

    # Send to Arduino in Proteus
    ser.write((data + "\n").encode())
    print("[FORWARDED TO PROTEUS]:", data)

    conn.close()
