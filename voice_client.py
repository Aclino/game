import socket
import speech_recognition as sr

UDP_IP = "172.31.21.126 "
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recognizer = sr.Recognizer()
microphone = sr.Microphone()

print("🎤 Dites une commande (décolle, atterris, monte, descend, stop...)")

while True:
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("\nParlez...")
        audio = recognizer.listen(source)

    try:
        commande = recognizer.recognize_google(audio, language="fr-FR").lower()
        print(f"➡️  Vous avez dit : {commande}")

        sock.sendto(commande.encode(), (UDP_IP, UDP_PORT))

        if "stop" in commande or "quitte" in commande:
            print("🛑 Fin du programme vocal")
            break

    except sr.UnknownValueError:
        print("❌ Je n'ai pas compris, répète.")
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
