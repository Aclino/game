import asyncio
from mavsdk import System
import speech_recognition as sr

async def main():
    print("Connexion au drone PX4...")
    drone = System()
    await drone.connect(system_address="udp://:14540")  # pour simulateur ou QGroundControl

    print("En attente de connexion au drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Drone connecté !")
            break

    # Initialisation de la reconnaissance vocale
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Dites une commande (ex : 'décolle', 'atterris', 'avance', 'monte', 'descends')")

    while True:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("\n🎤 Parlez maintenant...")
            audio = recognizer.listen(source)

        try:
            commande = recognizer.recognize_google(audio, language="fr-FR").lower()
            print(f"➡️  Vous avez dit : {commande}")

            # Détection des mots-clés
            if "décolle" in commande:
                print("-- Armement et décollage...")
                await drone.action.arm()
                await drone.action.takeoff()

            elif "atterris" in commande or "pose toi" in commande:
                print("-- Atterrissage...")
                await drone.action.land()

            elif "monte" in commande:
                print("-- Montée...")
                await drone.action.set_takeoff_altitude(5)

            elif "désarme" in commande or "coupe moteurs" in commande:
                print("-- Désarmement...")
                await drone.action.disarm()

            elif "stop" in commande or "quitte" in commande:
                print("-- Fin du contrôle vocal --")
                break

            else:
                print("❓ Commande non reconnue pour le drone.")

        except sr.UnknownValueError:
            print("❌ Je n'ai pas compris, répète s'il te plaît.")
        except Exception as e:
            print(f"⚠️ Erreur : {e}")

if __name__ == "__main__":
    asyncio.run(main())
