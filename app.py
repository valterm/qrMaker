import tkinter as tk
from tkinter import ttk
import qrcode
from PIL import Image, ImageTk
import threading
import qrcode.constants
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
import tkinter.filedialog 

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QrGen")
        self.qr_label = None
        self.timer = None
        self.delay = 0.2

        # QR Details
        self.qr_text = tk.StringVar()
        self.box_size_var = tk.IntVar()
        self.border_var = tk.IntVar()
        self.style_var = tk.StringVar()
        self.rounded_var = tk.BooleanVar()
        self.image_is_overlayed = tk.BooleanVar()
        self.overlay_image = None
        self.overlay_image_is_transparent = tk.BooleanVar()
        self.size = 200
        
        # Set Defaults
        self.qr_text.set("https://github.com/valterm")
        self.box_size_var.set(10)
        self.border_var.set(2)
        self.style_var.set("default")
        self.rounded_var.set(False)
        self.image_is_overlayed = False
        self.overlay_image_is_transparent.set(False)

        # Prettyfy
        # Set app icon to assets/icon.png
        self.root.iconbitmap("assets/icon.ico")

        # Layout
        # Centered Frame for the QR display
        self.qr_frame = ttk.Frame(self.root, padding=20)
        self.qr_frame.grid(row=0, column=1, pady=10)

        # Button to save the qr code
        self.save_button = ttk.Button(self.root, text="Save QR Code", command=self.save_qr_code)
        self.save_button.grid(row=1, column=1, pady=3, padx=10)

        # Input field with label "QR Code Text"
        self.input_label = ttk.Label(self.root, text="QR Code Text", anchor='w')
        self.input_label.grid(row=2, column=0, pady=3,)
        self.input_field = tk.Text(self.root, width=40, height=10)
        self.input_field.grid(row=2, column=1, pady=3, padx=10)
        self.input_field.bind("<KeyRelease>", self.start_timer)

        # Label "QR Styling", bold text, and padding
        self.style_label = ttk.Label(self.root, text="QR Styling", font=("TkDefaultFont", 18, "bold"), anchor='w')
        self.style_label.grid(row=3, column=0, pady=10, padx=20)

        # Dropdown for QR style
        self.style_label = ttk.Label(self.root, text="QR Style", anchor='w')
        self.style_label.grid(row=4, column=0, pady=3, padx=5)
        self.style_dropdown = ttk.Combobox(self.root, state="readonly", textvariable=self.style_var, values=["default", "rounded", "vertical", "horizontal"])
        self.style_dropdown.grid(row=4, column=1, pady=3)
        self.style_dropdown.bind("<<ComboboxSelected>>", self.start_timer)

        # Checkbox for rounded eyes
        self.rounded_label = ttk.Label(self.root, text="Rounded Eyes", anchor='w')
        self.rounded_label.grid(row=5, column=0, pady=3, padx=5)
        self.rounded_checkbox = ttk.Checkbutton(self.root, variable=self.rounded_var)
        self.rounded_checkbox.grid(row=5, column=1, pady=3)
        self.rounded_checkbox.bind("<Button-1>", self.start_timer)

        # Spinbox for box size and border size
        # self.box_size_label = ttk.Label(self.root, text="Box Size", anchor='w')
        # self.box_size_label.grid(row=6, column=0, pady=3, padx=5)
        self.border_label = ttk.Label(self.root, text="Border Size", anchor='w')
        self.border_label.grid(row=7, column=0, pady=3, padx=5)
        # self.box_size_entry = ttk.Spinbox(self.root, width=10, textvariable=self.box_size_var, from_=1, to=50, increment=1, state="NORMAL",command=self.start_timer)
        self.border_entry = ttk.Spinbox(self.root, width=10, textvariable=self.border_var, from_=0, to=50, increment=1, state="NORMAL",command=self.start_timer)
        # self.box_size_entry.grid(row=6, column=1, pady=3)
        self.border_entry.grid(row=7, column=1, pady=3)
        # self.box_size_entry.bind("<KeyRelease>", self.start_timer)
        # self.border_entry.bind("<KeyRelease>", self.start_timer)

        # Add a file selector to select an image to overlay
        self.logo = None
        self.logo = ttk.Label(self.root, text="Overlay Image", anchor='w')
        self.logo.grid(row=8, column=0, pady=3, padx=5)
        self.logo = ttk.Button(self.root, text="Select Image", command=self.select_overlay_image)
        self.logo.grid(row=8, column=1, pady=3)

        # Checkbox asking if the overlay image should be transparent
        self.transparent_checkbox = ttk.Checkbutton(self.root, text="Transparent image?", variable=self.overlay_image_is_transparent)
        self.transparent_checkbox.grid(row=8, column=2, pady=3, padx=10)
        self.transparent_checkbox.bind("<Button-1>", self.start_timer)

        # Add a clear image button
        self.clear_button = ttk.Button(self.root, text="Clear Image", command=self.clear_image)
        self.clear_button.grid(row=9, column=1, pady=0,)

        # Add a firendly message to bottom right corner saying "Made with <3 by circo"
        # self.message = ttk.Label(self.root, text="Made with ♥ by valterm", anchor='e', font=("TkDefaultFont", 6))
        # self.message.grid(row=10, column=0, pady=10, padx=10)

        # Display a default QR code initially
        self.update_qr()

    def update_qr(self):

        style_map = {
            "default": (None, None),
            "rounded": (RoundedModuleDrawer(), None),
            "vertical": (VerticalBarsDrawer(), None),
            "horizontal": (HorizontalBarsDrawer(), None),
        }

        text = self.qr_text.get()
        if not text:
            text = "https://github.com/valterm"

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=self.box_size_var.get(), border=self.border_var.get())
        qr.add_data(text)
        qr.make(fit=True)

        if self.image_is_overlayed:
            overlay = Image.open(self.overlay_image)
            if self.overlay_image_is_transparent.get():
                
                overlay_size = overlay.size
                overlay_size = (overlay_size[0] + int(overlay_size[0] * 0.05), overlay_size[1] + int(overlay_size[1] * 0.05))
                overlay_image = Image.new("RGBA", overlay_size, (255, 255, 255, 255))
                try:
                    overlay_image.paste(overlay, (int(overlay_size[0] * 0.025), int(overlay_size[1] * 0.025)), overlay)
                
                except ValueError as e:
                    overlay_image = overlay

                
            else:
                overlay_image = overlay

            # Create the qr code image with the embedded image
            img = qr.make_image(fill="black", back_color="white", image_factory=StyledPilImage, module_drawer=style_map[self.style_var.get()][0], eye_drawer=RoundedModuleDrawer(), embeded_image=overlay_image)

            # Cleanup
            overlay.close()


        else:
            img = qr.make_image(fill="black", back_color="white", image_factory=StyledPilImage, module_drawer=style_map[self.style_var.get()][0], eye_drawer=RoundedModuleDrawer() if self.rounded_var.get() else SquareModuleDrawer())

        img = img.resize((200, 200), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        if self.qr_label:
            self.qr_label.config(image=img)
            self.qr_label.image = img
        else:
            self.qr_label = ttk.Label(self.qr_frame, image=img)
            self.qr_label.image = img
            self.qr_label.grid(row=0, column=0)

    def start_timer(self, event=None):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.delay, self.set_properties_and_update_qr)
        self.timer.start()


    def set_properties_and_update_qr(self):
        # self.box_size_var.set(self.box_size_entry.get())
        print(self.overlay_image_is_transparent.get())
        self.border_var.set(self.border_entry.get())
        self.qr_text.set(self.input_field.get("1.0","end-1c"))
        self.update_qr()


    def select_overlay_image(self):
        # Open dialog window to select an image file
        image_path = tk.filedialog.askopenfilename(filetypes=[("Image File", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if image_path:
            self.overlay_image = image_path
            self.image_is_overlayed = True
            self.update_qr()
            

    def clear_image(self):
        self.overlay_image = None
        self.image_is_overlayed = False
        self.update_qr()

    def save_qr_code(self):
        # Create dialog to save the qr code
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        # Convert image to be saveable
        img = self.qr_label.image
        img = img._PhotoImage__photo.subsample(1, 1)
        img.write(file_path, format="png")



# Main app content
if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()

