# voice_client.py (Windows) — auto-detect WSL IP and test UDP
import socket
import subprocess
import speech_recognition as sr
import time

UDP_PORT = 5005

def get_wsl_ip():
    try:
        # ask WSL for its IP(s)
        out = subprocess.check_output(["wsl", "hostname", "-I"], universal_newlines=True).strip()
        if not out:
            return None
        # take first IP token
        ip = out.split()[0]
        return ip
    except Exception as e:
        print("Erreur get_wsl_ip:", e)
        return None

def udp_test_send(ip, msg="__udp_test__"):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(msg.encode(), (ip, UDP_PORT))
        sock.close()
        return True
    except Exception as e:
        print("UDP send error:", e)
        return False

def main():
    wsl_ip = get_wsl_ip()
    print("WSL IP détectée :", wsl_ip)
    if not wsl_ip:
        print("Impossible de détecter l'IP WSL. Assure-toi que 'wsl hostname -I' fonctionne.")
        return

    print("Envoi d'un message test UDP vers", f"{wsl_ip}:{UDP_PORT}")
    ok = udp_test_send(wsl_ip)
    print("Envoi UDP OK :", ok)
    if not ok:
        print("Vérifie le pare-feu Windows et que WSL écoute le port.")

    # if you want to continue with speech recognition:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Parle une commande (décolle, atterris, stop...)")
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Parle...")
            audio = recognizer.listen(source)
        try:
            cmd = recognizer.recognize_google(audio, language="fr-FR").lower()
            print("Reconnu:", cmd)
            sock.sendto(cmd.encode(), (wsl_ip, UDP_PORT))
            if "quitte" in cmd:
                print("Arrêt voice_client")
                break
        except sr.UnknownValueError:
            print("Non compris")
        except Exception as e:
            print("Erreur SR/UDP:", e)

if __name__ == "__main__":
    main()
