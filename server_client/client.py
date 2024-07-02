#!/usr/bin/env python
import io, dxcam, base64
from PIL import Image
import asyncio
from websockets.sync.client import connect


class ScreenCapture:
    
    def __init__(self, camera=None, buffer=None, fps=120) -> None:
        
        self.buffer = buffer if buffer else io.BytesIO()
        self.camera = camera if camera else dxcam.create()
        self.fps = fps

        self.setup_screen_height_and_width()
        self.start_recording(video_mode=True)

    def setup_screen_height_and_width(self):
        screenshot = self.camera.grab()
        SCREENSHOT_HEIGHT, SCREENSHOT_WIDTH, _ = screenshot.shape
        self.sh = SCREENSHOT_HEIGHT
        self.sw = SCREENSHOT_WIDTH
    
    def start_recording(self, video_mode=True):
        self.camera.start(target_fps=self.fps, video_mode=video_mode)

    def capture_screen(self) -> str:
        screenshot = self.camera.get_latest_frame()
        SCREENSHOT_RGB = screenshot.tobytes()

        # Convert to Image for processing
        img = Image.frombytes("RGB", (self.sw, self.sh), SCREENSHOT_RGB)
        # Save to in-memory bytes buffer
        
        img.save(self.buffer, format="PNG")
        self.buffer.seek(0)

        # Encode image to base64
        img_str = base64.b64encode(self.buffer.getvalue()).decode("utf-8")

        return img_str


def stream():
    with connect("ws://localhost:8765") as websocket:
        while True:

            frame = screen_capture.capture_screen()
            websocket.send(frame)
            status = websocket.recv()
            print(f"Status: {status}")

if __name__ == '__main__':
    screen_capture = ScreenCapture()
    stream()
