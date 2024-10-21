import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab, PngImagePlugin
import Quartz
import os
import json

# Cache last used directory and file
last_used_directory = None
last_used_filename = "screenshot.png"

def get_work_area_size():
    screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
    # The available width and height
    width = int(screen.size.width)
    height = int(screen.size.height)
    return width, height


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        screen_width, screen_height = get_work_area_size()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparent", True)

        self.root.config(bg="systemTransparent")

        self.start_x = None
        self.start_y = None
        self.rect = None

        # Capture mouse click and drag events
        self.root.bind("<ButtonPress-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)

        # Create a Canvas with transparent background
        self.canvas = tk.Canvas(
            self.root, cursor="cross", bg="systemTransparent", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_click(self, event):
        # Capture the starting x, y coordinates
        self.start_x = event.x
        self.start_y = event.y
        # Draw a rectangle
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="white"
        )

    def on_drag(self, event):
        # Update the rectangle as the user drags the mouse
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        # When the mouse is released, take the screenshot
        end_x, end_y = (event.x, event.y)
        self.root.withdraw()  # Hide the window

        # Take screenshot of the specified region
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        # Prepare metadata in JSON format
        metadata = {
            "startX": x1,
            "startY": y1,
            "width": x2 - x1,
            "height": y2 - y1,
        }

        # Open file dialog for saving with last used directory
        global last_used_directory, last_used_filename

        file_path = filedialog.asksaveasfilename(
            initialdir=last_used_directory if last_used_directory else os.getcwd(),
            initialfile=last_used_filename,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if file_path:
            # Update the last used directory and filename
            last_used_directory = os.path.dirname(file_path)
            last_used_filename = os.path.basename(file_path)

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # Convert screenshot to PNGImagePlugin object to modify EXIF
            metadata_comment = json.dumps(metadata)
            png_info = PngImagePlugin.PngInfo()
            png_info.add_text("Comment", metadata_comment)

            # Save the image with metadata (EXIF comment)
            screenshot.save(file_path, "PNG", pnginfo=png_info)

            print(
                f"Screenshot saved: {file_path} - Coordinates ({x1}, {y1}), Width: {x2-x1}, Height: {y2-y1}, EXIF data added: {metadata_comment}"
            )

        self.root.quit()


root = tk.Tk()
app = ScreenshotApp(root)
root.mainloop()

