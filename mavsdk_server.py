import asyncio
import socket
import subprocess
import threading

UDP_IP   = "0.0.0.0"
UDP_PORT = 5005

ROS2_SETUP   = "/opt/ros/jazzy/setup.bash"
ROS2_WS      = "/home/nico/LLM-controlled-drone"

def send_to_ai(commande_naturelle: str):
    """Publie une commande en langage naturel sur /user_command pour le brain_node."""
    ros_cmd = (
        f"source {ROS2_SETUP} && "
        f"source {ROS2_WS}/install/setup.bash && "
        f"ros2 topic pub /user_command std_msgs/msg/String "
        f"\"data: '{commande_naturelle}'\" --once"
    )
    print(f"  → IA : '{commande_naturelle}'")
    subprocess.Popen(
        ros_cmd,
        shell=True,
        executable="/bin/bash",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def traduire_commande(commande: str) -> str | None:
    """Traduit une commande vocale courte en instruction langage naturel pour l'IA."""
    c = commande.lower().strip()

    if "décolle" in c or "decolle" in c:
        return "Take off to 10 metres"
    elif "atterri" in c or "pose toi" in c or "atterris" in c:
        return "Land"
    elif "retour" in c or "rentre" in c or "rtl" in c:
        return "Return to launch"
    elif "monte" in c:
        # Essayer d'extraire un nombre : "monte 20" → 20m
        mots = c.split()
        for m in mots:
            if m.isdigit():
                return f"Fly to altitude {m} metres"
        return "Fly to altitude 20 metres"
    elif "descend" in c:
        mots = c.split()
        for m in mots:
            if m.isdigit():
                return f"Fly to altitude {m} metres"
        return "Fly to altitude 5 metres"
    elif "avance" in c:
        mots = c.split()
        for m in mots:
            if m.isdigit():
                return f"Go {m} metres north"
        return "Go 20 metres north"
    elif "recule" in c:
        mots = c.split()
        for m in mots:
            if m.isdigit():
                return f"Go {m} metres south"
        return "Go 20 metres south"
    elif "gauche" in c:
        return "Go 20 metres west"
    elif "droite" in c:
        return "Go 20 metres east"
    elif "tourne" in c or "pivote" in c:
        mots = c.split()
        for m in mots:
            if m.isdigit():
                return f"Set heading to {m} degrees"
        return "Rotate 90 degrees"
    elif "orbite" in c or "tourne autour" in c or "cercle" in c:
        return "Orbit around current position with radius 20 metres"
    elif "cherche" in c or "trouve" in c or "scan" in c:
        # Extraire l'objet : "cherche une personne" → "person"
        for mot, yolo in [("personne", "person"), ("voiture", "car"),
                           ("camion", "truck"), ("vélo", "bicycle"),
                           ("chien", "dog"), ("chat", "cat")]:
            if mot in c:
                return f"Search for a {yolo}"
        return "Search and scan the area"
    elif "stop" in c or "stoppe" in c or "arrête" in c or "freeze" in c:
        return "Hold position"
    elif "désarme" in c or "coupe" in c:
        return "Disarm"
    elif c.startswith("ia:") or c.startswith("ai:"):
        # Mode direct : "ia: survole le lac à 50 mètres"
        return c.split(":", 1)[1].strip()
    else:
        # Passer la commande directement à l'IA sans traduction
        return commande.strip()

async def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print("╔══════════════════════════════════════╗")
    print("║   🚁 Serveur commandes drone (IA)    ║")
    print(f"║   UDP {UDP_IP}:{UDP_PORT}                   ║")
    print("║   Commandes → brain_node via ROS2    ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Commandes disponibles :")
    print("  décolle / atterri / stop / retour")
    print("  monte [m] / descend [m]")
    print("  avance [m] / recule [m] / gauche / droite")
    print("  orbite / cherche [objet] / scan")
    print("  ia: <texte libre>  → envoi direct à l'IA")
    print()
    print("En attente de commandes UDP...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            commande_brute = data.decode().strip()
            print(f"\n📥 Reçu de {addr[0]} : '{commande_brute}'")

            if "quitte" in commande_brute.lower() or "quit" in commande_brute.lower():
                print("Arrêt du serveur.")
                break

            instruction = traduire_commande(commande_brute)
            if instruction:
                send_to_ai(instruction)
            else:
                print("  ⚠️  Commande non reconnue")

        except BlockingIOError:
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
