import tkinter as tk
from PIL import Image, ImageTk
import os

class MainScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Main Screen")

        # Set maximum window dimensions
        self.max_width = 800
        self.max_height = 800

        # Get the path to the image, assuming repo was cloned correctly
        script_dir = os.path.dirname(__file__)
        img_path = os.path.join(script_dir, 'MainScreen.png')

        # Open the image using Pillow
        try:
            original_image = Image.open(img_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.root.destroy()
            return

        # Calculate a scale factor so the image fits within the max dimensions while preserving aspect ratio.
        scale_factor = min(self.max_width / original_image.width,
                           self.max_height / original_image.height,
                           1.0)
        self.new_width = int(original_image.width * scale_factor)
        self.new_height = int(original_image.height * scale_factor)

        # Resize the image using high-quality resampling.
        resized_image = original_image.resize((self.new_width, self.new_height), resample=Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized_image)

        # Create a canvas that exactly fits the resized image.
        self.canvas = tk.Canvas(self.root, width=self.new_width, height=self.new_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

        # Define the invisible clickable area in the bottom left.
        rect_width = 300  
        rect_height = 200  #
        x0 = 0
        y0 = self.new_height - rect_height
        x1 = rect_width
        y1 = self.new_height

        # Create the invisible rectangle (no fill or outline).
        rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill="", outline="")
        # Bind a click event to the rectangle.
        self.canvas.tag_bind(rect_id, "<Button-1>", self.switch_window)

    def switch_window(self, event):
        print("Invisible clickable area clicked. Switching windows...")
        # Hide the main window.
        self.root.withdraw()
        # Create a new window 
        second_window = tk.Toplevel()
        second_window.title("Second Window")
        second_window.geometry(f"{self.new_width}x{self.new_height}")

        # Add content to the second window.
        label = tk.Label(second_window, text="This is the second window!")
        label.pack(padx=20, pady=20)

        # Optionally, when the second window is closed, re-show the main window.
        def on_close():
            second_window.destroy()
            self.root.deiconify()
        second_window.protocol("WM_DELETE_WINDOW", on_close)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MainScreen()
    app.run()
