import asyncio 
import socket
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityNedYaw

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

async def main():
    print("Connexion au drone PX4...")
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("En attente de connexion MAVSDK...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connecté !")
            break

    # UDP listener socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print("En attente de commandes vocales...")

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            commande = data.decode().lower()
            print(f"Commande reçue : {commande}")

            if "décolle" in commande:
                print("Décollage...")
                await drone.action.arm()
                await drone.action.takeoff()

            elif "atterri" in commande or "pose toi" in commande:
                print("Atterrissage")
                await drone.action.land()

            elif "monte" in commande:
                print("Montée")
                await drone.action.set_takeoff_altitude(5)

            elif "descend" in commande:
                print("Descente")
                await drone.action.set_takeoff_altitude(0)

            elif "désarme" in commande or "coupe" in commande:
                print("Désarmement")
                await drone.action.disarm()

            elif "avance" in commande:
                print("Avance ")

                # Définition d’un setpoint initial obligatoire
                try:
                    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                    await drone.offboard.start()
                except OffboardError as e:
                    print(f"Erreur Offboard : {e._result.result}")
                    continue

                # Avancer : X positif → 1 m/s pendant 1 seconde
                await drone.offboard.set_velocity_ned(VelocityNedYaw(1.0, 0.0, 0.0, 0.0))
            elif "recule" in commande:
                try:
                    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                    await drone.offboard.start()
                except OffboardError as e:
                    print(f"Erreur Offboard : {e._result.result}")
                    continue
                    await drone.offboard.set_velocity_ned(VelocityNedYaw(-1.0, 0.0, 0.0, 0.0))
            elif "stoppe" in commande:
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                await drone.offboard.stop()
            elif "quitte" in commande:
                print ("Arret des commande")
                break

            else:
                print("Commande non reconnue")

        except BlockingIOError:
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
