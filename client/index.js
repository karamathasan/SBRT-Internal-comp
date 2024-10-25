document.addEventListener('DOMContentLoaded', async (event) => {
    const joystick = document.getElementsByClassName('joystick')[0];
    const stick = document.getElementsByClassName('stick')[0];
    let radius = 100;
    let dragging = false;
    let animationFrameId = null;

    // Initialize WebSocket connection
    let socket = new WebSocket("ws://192.168.1.49:80/motion");

    socket.addEventListener("open", () => {
        //socket.send("Hello Server!");
    });

    const resetStickPosition = () => {
        stick.style.top = '100px';
        stick.style.left = '100px';
    };

    const moveStick = (x, y) => {
        stick.style.top = `${y + radius}px`;
        stick.style.left = `${x + radius}px`;

        console.log("x:" + x + ", y:" + y);
        // Send coordinates via WebSocket
        if (socket.readyState === WebSocket.OPEN) {
            socket.send([x, -y]);
        }
    };

    const handleMovement = (clientX, clientY) => {
        const rect = joystick.getBoundingClientRect();
        let x = clientX - rect.left - 100; // Offset to center (range: -75 to 75)
        let y = clientY - rect.top - 100;

        // Constrain values between -75 and 75
        x = Math.max(-radius, Math.min(x, radius));
        y = Math.max(-radius, Math.min(y, radius));

        let current_radius = Math.sqrt(x*x + y*y); 
        if(current_radius <= radius){
            // Request a frame update to move the stick
            if (!animationFrameId) {
                animationFrameId = requestAnimationFrame(() => {
                    moveStick(x, y);
                    animationFrameId = null; // Reset after rendering
                });
            }
        }
    };

    // Enable dragging of joystick on touchdown/mousedown
    stick.addEventListener('mousedown', (e) => {
        dragging = true;
    });

    // Disable dragging and reset position of joystick on touchdown/mouseup
    document.addEventListener('mouseup', () => {
        if (dragging) {
            dragging = false;
            resetStickPosition();
            moveStick(0,0)
        }
    });

    // Update position of joystick and send new movement to ESP32 on touchmove/mousemove
    document.addEventListener('mousemove', (e) => {
        if (dragging) {
            handleMovement(e.clientX, e.clientY);
        }
    });
});