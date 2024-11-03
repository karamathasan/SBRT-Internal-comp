from microdot import Microdot
from microdot.websocket import with_websocket
from microdot.cors import CORS
from machine import Pin, PWM
import ujson
import asyncio 
import network
import env
import time

print("board start")
LED = Pin("LED",Pin.OUT)
LED.toggle()


# motor 1 is LF, motor 2 is LB
# motor 3 is RB, motor 4 is LF
LFen = PWM(Pin(3, Pin.OUT), freq=1000)
LBen = PWM(Pin(11, Pin.OUT), freq=1000)

RFen = PWM(Pin(7, Pin.OUT), freq=1000)
RBen = PWM(Pin(13, Pin.OUT), freq=1000)

LFin1 = Pin(0,Pin.OUT)
LFin2 = Pin(10,Pin.OUT)
LBin1 = Pin(5,Pin.OUT)
LBin2 = Pin(9,Pin.OUT)

RFin1 = Pin(26,Pin.OUT)
RFin2 = Pin(22,Pin.OUT)
RBin1 = Pin(20,Pin.OUT)
RBin2 = Pin(21,Pin.OUT)

servo = PWM(Pin(17,Pin.OUT))
# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(env.SSID, env.PASSWORD)
time.sleep(5)

# Wait for connection
max_attempts = 10
attempt = 0
print("attempting connection . . . ")
while not wlan.isconnected() and attempt < max_attempts:
    print(f"Trying to connect to env.SSID (Attempt {attempt + 1}/{max_attempts})...")
    time.sleep(10)
    attempt += 1

if wlan.isconnected():
    print("Connected to IP:", wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi. Please check your SSID and password.")


app = Microdot()
CORS(app, allowed_origins = '*', allow_credentials = True)

def drive(left, right):
    """
    sets the appropriate motor inputs from the controller outputs
    - Parameters: 
        - left: float > left stick inputs
        - right: float > right stick inputs
    """

    # left side assignment
    if left > 0:
        LFin1.value(1)
        LFin2.value(0)
        LBin1.value(1)
        LBin2.value(0)
    elif left < 0:
        LFin1.value(0)
        LFin2.value(1)
        LBin1.value(0)
        LBin2.value(1)
    else:
        LFin1.value(0)
        LFin2.value(0)
        LBin1.value(0)
        LBin2.value(0)

    if right > 0:
        RFin1.value(1)
        RFin2.value(0)
        RBin1.value(1)
        RBin2.value(0)
    elif right < 0:
        RFin1.value(0)
        RFin2.value(1)
        RBin1.value(0)
        RBin2.value(1)
    else:
        RFin1.value(0)
        RFin2.value(0)
        RBin1.value(0)
        RBin2.value(0)       
    
    if abs(left) < 0.15:
        left = 0
    if abs(right) < 0.15:
        right = 0
    
    LFen.duty_u16(int(abs(left) * 65535))
    LBen.duty_u16(int(abs(left) * 65535))
    RFen.duty_u16(int(abs(right) * 65535))
    RBen.duty_u16(int(abs(right) * 65535))

@app.route('/hello_world', methods=['GET'])
async def get_invoices(request):
    return 'Hello World!'

@app.get('/')
@with_websocket
async def index(request, ws):
    try: 
        while True:
            data = await ws.receive()
            if not data:
                break
            await ws.send('hello world')
            
    except OSError as msg:
        print(msg)

@app.get('/drive')
@with_websocket
async def index(request, ws):
    # drives the robot based on motor inputs
    # when the left or right sides are positive inputs, 
    
    while True:
        data = await ws.receive()
        if not data:
            break
        inputs = ujson.loads(data)
        drive(0,0)
        drive(inputs["left"], inputs["right"])
        
@app.get("/msgs")
@with_websocket
async def index(request, ws):
    while True:
        data = await ws.receive()
        print(data)

@app.get("/action")
@with_websocket
async def index(request, ws):
    while True:
        data = await ws.receive()
        data = ujson.loads(data)
        val = data[value]
        servo.duty_u16(int(val * 65535))
app.run(port=80)

