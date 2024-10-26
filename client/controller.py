import asyncio
import pygame
import keyboard
import websockets
import json

# pygame setup

pygame.init()
joystick = pygame.joystick.Joystick(0)
# rightStick = pygame.joystick.Joystick(1)
pygame.joystick.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

async def websocket_client(queue):
    async with websockets.connect("ws://192.168.1.61:80/msgs") as websocket:
        print("Connected to WebSocket server.")
        while True:
            # Wait for a message from the Pygame event loop
            action = await queue.get()
            
            if action == "quit":
                break
            
            # Send the action to the WebSocket server
            await websocket.send(json.dumps({"action": action}))
            # print(f"Sent action: {action}")

async def main():
    queue = asyncio.Queue()
    websocket_task = asyncio.create_task(websocket_client(queue))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                await queue.put("quit")  # Tell WebSocket client to close
                websocket_task.cancel()
                break

            # Detect specific button press (e.g., button 0)
            elif event.type == pygame.JOYAXISMOTION:
                res = await queue.put(json.dumps({"left":str(joystick.get_axis(1)),"right":str(joystick.get_axis(3))}))
                print({"left":str(joystick.get_axis(1)),"right":str(joystick.get_axis(3))})
                

        # Update Pygame display (optional)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        
        await asyncio.sleep(0.01)  # Small delay for Pygame event handling

    await websocket_task

# Run the event loop
asyncio.run(main())

pygame.quit()

# async def start_client():
#     async with websockets.connect("ws://192.168.1.61:80/msgs") as websocket:
#         while True:
#             if keyboard.is_pressed("space"):
#                 await websocket.send("buzz")

#             if keyboard.is_pressed("q"):
#                 print("end running")
#                 break
                
# async def drive():
#     async with websockets.connect("ws://192.168.1.61:80/drive") as websocket:
#         while True:
#             if keyboard.is_pressed("a"):
#                 await websocket.send(json.dumps({"left":"0","right":"0"}))
#                 break

# if __name__ == "__main__":
#     asyncio.run(start_client()) 
