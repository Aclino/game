"""
voice_client.py (Windows) — Push-to-talk vers drone IA via UDP/WSL

Maintenir ESPACE enfoncé pour parler, relâcher pour envoyer.
"""

import socket
import subprocess
import threading
import sys
import time
import speech_recognition as sr

# ─── Config ───────────────────────────────────────────────────────────────────

UDP_PORT    = 5005
LANGUAGE    = "fr-FR"       # langue de reconnaissance
HOLD_KEY    = "space"       # touche push-to-talk (espace)
ENERGY_THRESHOLD = 300      # sensibilité micro (baisser si micro faible)

# ─── Détection IP WSL ─────────────────────────────────────────────────────────

def get_wsl_ip():
    try:
        out = subprocess.check_output(
            ["wsl", "hostname", "-I"], universal_newlines=True
        ).strip()
        return out.split()[0] if out else None
    except Exception as e:
        print(f"Erreur get_wsl_ip: {e}")
        return None

# ─── Envoi UDP ────────────────────────────────────────────────────────────────

def udp_send(sock, ip, message):
    try:
        sock.sendto(message.encode(), (ip, UDP_PORT))
        print(f"  📤 Envoyé : '{message}'")
    except Exception as e:
        print(f"  ❌ Erreur UDP : {e}")

# ─── Push-to-talk avec pynput ─────────────────────────────────────────────────

try:
    from pynput import keyboard
    PYNPUT_OK = True
except ImportError:
    PYNPUT_OK = False

def push_to_talk(sock, wsl_ip):
    """Mode push-to-talk : maintenir ESPACE pour enregistrer."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = ENERGY_THRESHOLD
    recognizer.dynamic_energy_threshold = True

    print("\n🎙️  Mode Push-to-Talk")
    print(f"   Maintenir [ESPACE] pour parler, relâcher pour envoyer")
    print(f"   Appuyer sur [Q] pour quitter\n")

    is_recording   = False
    stop_listening = None
    audio_buffer   = []

    def on_press(key):
        nonlocal is_recording, stop_listening
        try:
            if key == keyboard.Key.space and not is_recording:
                is_recording = True
                audio_buffer.clear()
                print("🔴 Enregistrement... (relâche pour envoyer)")
                # Démarrer écoute en arrière-plan
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, phrase_time_limit=10)
                    audio_buffer.append(audio)

            elif hasattr(key, 'char') and key.char == 'q':
                print("\n👋 Arrêt du client vocal.")
                return False  # stop listener

        except Exception as e:
            print(f"  Erreur on_press : {e}")

    def on_release(key):
        nonlocal is_recording
        if key == keyboard.Key.space and is_recording:
            is_recording = False
            print("⏹️  Traitement...")
            if audio_buffer:
                try:
                    cmd = recognizer.recognize_google(
                        audio_buffer[0], language=LANGUAGE
                    ).lower()
                    print(f"✅ Reconnu : '{cmd}'")
                    udp_send(sock, wsl_ip, cmd)
                    if "quitte" in cmd or "quit" in cmd:
                        return False
                except sr.UnknownValueError:
                    print("❓ Non compris — réessaie")
                except sr.RequestError as e:
                    print(f"❌ Erreur Google SR : {e}")
                    print("   (vérifie ta connexion internet)")

    # Lancer le listener clavier
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def fallback_input_mode(sock, wsl_ip):
    """Mode texte si pynput non disponible."""
    print("\n⌨️  Mode texte (pynput non installé)")
    print("   Tape ta commande et appuie sur Entrée")
    print("   'quitte' pour arrêter\n")
    while True:
        try:
            cmd = input("Commande > ").strip().lower()
            if not cmd:
                continue
            udp_send(sock, wsl_ip, cmd)
            if "quitte" in cmd:
                break
        except (KeyboardInterrupt, EOFError):
            break

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════╗")
    print("║   🚁 Client Vocal Drone (Push-to-Talk)   ║")
    print("╚══════════════════════════════════════════╝\n")

    # Détecter IP WSL
    wsl_ip = get_wsl_ip()
    if wsl_ip:
        print(f"✅ IP WSL détectée : {wsl_ip}")
    else:
        wsl_ip = input("IP WSL non détectée. Entre l'IP manuellement : ").strip()

    # Test connexion UDP
    print(f"📡 Test connexion vers {wsl_ip}:{UDP_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(b"__ping__", (wsl_ip, UDP_PORT))
        print("✅ UDP OK\n")
    except Exception as e:
        print(f"❌ UDP échoué : {e}")
        print("   Vérifie le pare-feu Windows et que mavsdk_server.py tourne dans WSL")
        return

    # Vérifier pynput
    if not PYNPUT_OK:
        print("⚠️  pynput non installé — mode texte activé")
        print("   Pour le mode vocal : pip install pynput\n")
        fallback_input_mode(sock, wsl_ip)
        return

    # Vérifier speech_recognition
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ speech_recognition non installé")
        print("   pip install SpeechRecognition pyaudio")
        return

    push_to_talk(sock, wsl_ip)
    sock.close()

if __name__ == "__main__":
    main()
