from mavsdk import System
import asyncio

async def test():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("connecting…")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ CONNECTÉ")
            break
    print("Décollage test…")
    await drone.action.arm()
    await drone.action.takeoff()

asyncio.run(test())
