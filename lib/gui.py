import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.filedialog
import threading
import os, sys
import logging

# Setup logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Ui:
    def __init__(self, qrfactory):
        self.root = tk.Tk()
        self.root.title("QR Creator")

        # QR Details
        self.qr_text = tk.StringVar()
        self.qr_label = None
        self.border_var = tk.IntVar()
        self.style_var = tk.StringVar()
        self.rounded_var = tk.BooleanVar()
        self.image_is_overlaid = tk.BooleanVar()
        self.overlay_image_is_transparent = tk.BooleanVar()
        self.size = tk.IntVar()
        self.delay = 0.2
        self.qrfactory = qrfactory
        self.timer = None
        # self.overlay_image = tk.StringVar()
        self.overlay_image = ""
        self.shrink_image = tk.BooleanVar()
        
        # Set Defaults
        self.qr_text.set("https://github.com/valterm")
        self.size.set(200)
        self.border_var.set(2)
        self.style_var.set("default")
        self.rounded_var.set(False)
        self.image_is_overlaid = False
        
        # Prettyfy
        # Set app icon to assets/icon.png
        icon_path = resource_path('assets/icon.ico')
        self.root.iconbitmap(icon_path)

        # Layout
        self.qr_frame = ttk.Frame(self.root)
        self.qr_frame.grid(row=0, column=4, padx=10, rowspan=80)
        
        # sep = ttk.Separator(self.root,orient='vertical')
        # sep.grid(row=0, column=3, rowspan=400, sticky='ns', padx=10, pady = 30)

        # Button to save the qr code
        self.save_button = ttk.Button(self.root, text="Save QR Code", command=self.save_qr_code)
        self.save_button.grid(row=80, column=4)

        # Input field with label "QR Code Text"
        self.qr_text_label = ttk.Label(self.root, text="QR Code Text", anchor='s')
        self.qr_text_label.grid(row=20, column=0, padx=10)
        self.qr_text_entry = tk.Text(self.root, width=40, height=10)
        self.qr_text_entry.grid(row=20, column=1, columnspan=2, pady=10)
        self.qr_text_entry.bind("<KeyRelease>", self.start_timer)

        # Dropdown for QR style
        self.style_label = ttk.Label(self.root, text="QR Style", anchor='w')
        self.style_label.grid(row=40, column=0)
        self.style_dropdown = ttk.Combobox(self.root, state="readonly", 
                                           textvariable=self.style_var, 
                                           values=["default", "rounded", "vertical", "horizontal", "gapped-squares", "circles"], width=14)
        self.style_dropdown.grid(row=40, column=1)
        self.style_dropdown.bind("<<ComboboxSelected>>", self.start_timer)

        self.transparent_checkbox = ttk.Checkbutton(self.root, text="Rounded Eyes", variable=self.rounded_var)
        self.transparent_checkbox.grid(row=40, column=2)
        self.transparent_checkbox.bind("<Button-1>", self.start_timer)

        # Spinbox for box size and border size
        self.border_label = ttk.Label(self.root, text="Border Size", anchor='w')
        self.border_label.grid(row=70, column=0)
        self.border_entry = ttk.Spinbox(self.root, width=10, textvariable=self.border_var, from_=0, to=50, increment=1, state="NORMAL",command=self.start_timer)
        self.border_entry.grid(row=70, column=1, pady=3)
        self.border_entry.bind("<KeyRelease>", self.start_timer)

        # Add a file selector to select an image to overlay
        self.logo = None
        self.logo = ttk.Label(self.root, text="Overlay Image", anchor='w')
        self.logo.grid(row=80, column=0)
        self.logo = ttk.Button(self.root, text="Select Image", command=self.select_overlay_image, width=10)
        self.logo.grid(row=80, column=1)

        # Checkbox asking if the overlay image should be transparent
        self.transparent_checkbox = ttk.Checkbutton(self.root, text="Transparent Image", variable=self.overlay_image_is_transparent)
        self.transparent_checkbox.grid(row=90, column=1, padx=10)
        self.transparent_checkbox.bind("<Button-1>", self.start_timer)

        # Checkbox to shrink image
        self.shrink_checkbox = ttk.Checkbutton(self.root, text="Shrink Image", variable=self.shrink_image)
        self.shrink_checkbox.grid(row=90, column=2, padx=10)
        self.shrink_checkbox.bind("<Button-1>", self.start_timer)

        # Add a clear image button
        self.clear_button = ttk.Button(self.root, text="Clear Image", command=self.clear_image, width=10)
        self.clear_button.grid(row=80, column=2)

        self.empty = ttk.Label(self.root, text="", anchor='w')
        self.empty.grid(row=100, column=0)

        logger.debug("Ui initialized")

    def start_timer(self, event=None):
        logger.debug("Starting timer")
        if self.timer:
            logging.debug("Destroying existing timer")
            self.timer.cancel()
        logger.debug("Starting timer thread")
        self.timer = threading.Timer(self.delay, self.get_data_and_update_qr)
        self.timer.start()

    def get_data_and_update_qr(self):
        logger.debug("Getting data and updating qr")
        self.qrfactory.set_qr_property("overlay_image_is_transparent", self.overlay_image_is_transparent.get())
        self.qrfactory.set_qr_property("overlay_image", self.overlay_image)
        self.qrfactory.set_qr_property("qr_text", self.qr_text_entry.get("1.0", "end-1c"))
        self.qrfactory.set_qr_property("qr_size", self.size.get())
        self.qrfactory.set_qr_property("border", self.border_var.get())
        self.qrfactory.set_qr_property("style", self.style_var.get())
        self.qrfactory.set_qr_property("rounded_eyes", self.rounded_var.get())
        self.qrfactory.set_qr_property("image_is_overlaid", self.image_is_overlaid)
        self.qrfactory.set_qr_property("shrink_overlay", self.shrink_image.get())
        self.qrfactory.update_qr()
        img = ImageTk.PhotoImage(self.qrfactory.return_qr_image())
        self.display_qr(img)

    def display_qr(self, img):
        logger.debug("Displaying QR")
        if self.qr_label:
            self.qr_label.config(image=img)
            self.qr_label.image = img
        else:
            self.qr_label = ttk.Label(self.qr_frame, image=img)
            self.qr_label.image = img
            self.qr_label.grid(row=0, column=0)        

    def start(self):
        logger.debug("Starting UI")
        self.get_data_and_update_qr()
        self.root.mainloop()

    def save_qr_code(self):
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.qrfactory.return_qr_image().save(file_path, "PNG")

        
    def select_overlay_image(self):
        image_path = tk.filedialog.askopenfilename(filetypes=[("Image File", "*.png *.jpg *.jpeg *.gif *.bmp")])
        logging.debug(f"Selected image: {image_path}")
        if image_path:
            self.overlay_image = image_path
            self.image_is_overlaid = True
            self.start_timer()
    
    def clear_image(self):
        # self.overlay_image = None
        self.overlay_image = ""
        self.image_is_overlaid = False
        self.start_timer()
    


        # @DEBUG

        # qrfactory.set_qr_property_and_update_qr("qr_text", "lel")
        # x = qrfactory.get_qr_image()
        # x.show()
