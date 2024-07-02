import network
import socket
import uasyncio as asyncio
import _thread
import base64

SSID = 'esp32-wifi-1'
PASSWORD = None  # Open network, no password

def create_hotspot():
    """Create a hotspot so devices can connect to this WiFi zone"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)
    while not ap.active():
        pass
    print('Network config:', ap.ifconfig())

async def echo(reader, writer):
    """Receive image over websocket and thread it to ESP32 SECOND CORE to be transmitted to VGA monitor"""
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break

            image = data.decode('utf-8')
            _thread.start_new_thread(send_through_vga, (image,))
            status = '200'
            writer.write(status.encode('utf-8'))
            await writer.drain()
        except Exception as e:
            print("Error:", e)
            break
    writer.close()
    await writer.wait_closed()

def send_through_vga(image):
    """Receive image as string, decode to base64 and send it over VGA"""
    try:
        image_data = base64.b64decode(image)
        # Use existing libraries to transmit "image_data" over VGA to be displayed on a connected monitor
        pass
    except Exception as e:
        print("Error decoding image:", e)

async def main():
    """Start WebSocket server to receive images, run in main core"""
    create_hotspot()
    
    server = await asyncio.start_server(echo, "0.0.0.0", 8765)
    addr = server.sockets[0].getsockname()
    print('Serving on', addr)
    
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped")
