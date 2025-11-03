import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("⏳ En attente de messages UDP...")

while True:
    data, addr = sock.recvfrom(1024)
    print("📩 Reçu:", data.decode())
