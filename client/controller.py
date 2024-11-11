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

height = 300
width = 400
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
ip = "192.168.1.61"
# ip = "192.168.1.77"

# phone ip: 192.168.160.99

def UI(left, right):
    pygame.draw.line(screen,"red",pygame.Vector2(width/2 - 50,height/2), pygame.Vector2(width/2 - 50, left * 100 + height/2), 25)
    pygame.draw.line(screen,"blue",pygame.Vector2(width/2 + 50,height/2), pygame.Vector2(width/2 + 50, right * 100 + height/2), 25)

async def quit(queue):
    await queue.put(json.dumps({"left":0,"right":0}))
    await queue.put("quit")  # Tell WebSocket client to close

async def drive_client(motion):
    async with websockets.connect(f"ws://{ip}:80/drive") as websocket:
        print("Connected to Drive server")
        while running:
            inputs = await motion.get()
            if inputs == "quit":
                break
            
            await websocket.send(inputs)

async def servo_client(servo):
    async with websockets.connect(f"ws://{ip}:80/servo") as websocket:
        print("Connected to Servo server")
        while running:
            inputs = await servo.get()
            if inputs == "quit":
                break
            
            await websocket.send(inputs)


async def main():
    servoDown = False
    motionQueue = asyncio.Queue()
    servoQueue = asyncio.Queue()
    drive_task = asyncio.create_task(drive_client(motionQueue))
    servo_task = asyncio.create_task(servo_client(servoQueue))
    
    running = True
    leftOld = joystick.get_axis(1)
    rightOld = joystick.get_axis(3)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                await quit(motionQueue)
                drive_task.cancel()
                servo_task.cancel()
                running = False
                break

            elif event.type == pygame.JOYAXISMOTION:
                leftDelta = joystick.get_axis(1) - leftOld
                leftOld = joystick.get_axis(1)
                rightDelta = joystick.get_axis(3) - rightOld
                rightOld = joystick.get_axis(3)
                if abs(leftDelta) > 0.005 or abs(rightDelta) > 0.005:
                    data = json.dumps(
                        {
                            "left":(round(joystick.get_axis(1),4)),
                            "right":(round(joystick.get_axis(3),4))
                        }
                    )
                    await motionQueue.put(data)

            elif event.type == pygame.JOYBUTTONDOWN: 
                if event.button == 10:
                    data = json.dumps({"servo":0})
                    if servoDown == False:
                        data = json.dumps(
                            {"servo":50}
                        )
                        servoDown = True
                    else:
                        data = json.dumps(
                            {"servo":0}
                        )
                        servoDown = False
                    print(f"right bumper pressed: {servoDown}")
                    await servoQueue.put(data)
                    if servoDown == True:
                        await asyncio.sleep(0.3)
                        await servoQueue.put(json.dumps({"servo":30}))

                if event.button == 9:
                    print("left shoulder pressed")


            # elif event.type == pygame.JOYBUTTONUP:
            #     if event.button == 10:
            #         data = json.dumps(
            #             {"servo":0}
            #         )
            #         await servoQueue.put(data)
                
        screen.fill((0, 0, 0))
        UI(joystick.get_axis(1),joystick.get_axis(3))
        pygame.display.flip()
        
        await asyncio.sleep(0.01)
    await drive_task
    await servo_task

# Run the event loop
asyncio.run(main())
3
pygame.quit()