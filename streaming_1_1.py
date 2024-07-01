""" UTILIZANDO DXCAM EN LUGAR DE MSS"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import dxcam
import time
from PIL import Image
import io
import base64

app = FastAPI()

# Add CORS middleware to allow connections from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, modify as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

buffer = io.BytesIO()
# Create an mss instance for capturing the screen
camera = dxcam.create()
camera.start(target_fps=120, video_mode=True)

@app.get("/")
async def root():
    return {"message": "Navigate to /ws to start screen streaming via WebSocket"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Capture the screen
            screenshot = camera.get_latest_frame()
            # Extract width, height, and RGB values
            SCREENSHOT_HEIGHT, SCREENSHOT_WIDTH, _ = screenshot.shape
            SCREENSHOT_RGB = screenshot.tobytes()

            # Convert to Image for processing
            img = Image.frombytes("RGB", (SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT), SCREENSHOT_RGB)

            # Save to in-memory bytes buffer
            
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode image to base64
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

            #print(img_str)

            # Send the base64 string to the client
            await websocket.send_text(img_str)

            
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)