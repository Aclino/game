# udp_listener.py (WSL)
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print("UDP listener en écoute sur 0.0.0.0:5005")
while True:
    data, addr = sock.recvfrom(4096)
    print("RECU de", addr, "->", data.decode())
