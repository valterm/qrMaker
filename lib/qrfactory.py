import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from PIL import Image
import logging

# Setup logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class QrFactory:
    def __init__(self):
        self.qr_text = ""
        self.qr_size = 500
        self.border = 2
        self.style = "default"
        self.rounded_eyes = False
        self.image_is_overlaid = False
        self.overlay_image = ""
        self.overlay_size = 0
        self.qr_image = None
        self.timer = None
        self.overlay_image_is_transparent = False
        self.shrink_overlay = False

        self.style_map = {
            "default": None,
            "rounded": RoundedModuleDrawer(),
            "gapped-squares": GappedSquareModuleDrawer(),
            "circles": CircleModuleDrawer(),
            "rounded": RoundedModuleDrawer(),
            "vertical": VerticalBarsDrawer(),
            "horizontal": HorizontalBarsDrawer(),
        }

        # debug logging 
        logging.debug("QrFactory initialized")

    def set_qr_property(self, property, value):
        # logging
        logger.debug(f"Setting {property} to {value}")
        setattr(self, property, value)
        # self.update_qr()

    def update_qr(self):
        text = self.qr_text
        if not text:
            text = "https://github.com/valterm"
        
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, 
                           border=self.border)
        qr.add_data(text)
        qr.make(fit=True)

        if self.image_is_overlaid:
            logger.debug(f"Overlaying image {self.overlay_image}")
            overlay = Image.open(self.overlay_image)
            if self.overlay_image_is_transparent:
                box_size = overlay.size
                # overlay_size = (overlay_size[0] + int(overlay_size[0] * 0.05), overlay_size[1] + int(overlay_size[1] * 0.05))
                box = Image.new("RGBA", box_size, (255, 255, 255, 255))
                try:
                    # Paste the overlay image into the center of the white box
                    box.paste(overlay, (0, 0), overlay)
                    overlay_image = box

                    # overlay_image.paste(overlay, (int(overlay_size[0]), int(overlay_size[1])), overlay)
                except ValueError as e:
                    logger.error(f"Error overlaying image: {e}")
                    overlay_image = overlay
            else:
                overlay_image = overlay

            if self.shrink_overlay:
                img = qr.make_image(fill="black", back_color="white", 
                                image_factory=StyledPilImage, 
                                module_drawer=self.style_map[self.style], 
                                eye_drawer=RoundedModuleDrawer() if self.rounded_eyes else SquareModuleDrawer())
                # Shrink overlay_image to 10% of the qr code size
                overlay_image = overlay_image.resize((int(self.qr_size * 0.23), int(self.qr_size * 0.23)), Image.LANCZOS)
                logger.debug(f"Overlay image size: {overlay_image.size}")
                

                # Paste the shrunken image into the center
                img.paste(overlay_image, ((img.size[0]-overlay_image.size[0])//2, (img.size[1]-overlay_image.size[1])//2), overlay_image)

            else:
                img = qr.make_image(fill="black", back_color="white", 
                                    image_factory=StyledPilImage, 
                                    module_drawer=self.style_map[self.style], 
                                    eye_drawer=RoundedModuleDrawer() if self.rounded_eyes else SquareModuleDrawer(), 
                                    embeded_image=overlay_image)
                logger.debug(f"Overlay image size: {overlay_image.size}")

            overlay.close()
        else:
            img = qr.make_image(fill="black", back_color="white", 
                                image_factory=StyledPilImage, 
                                module_drawer=self.style_map[self.style], 
                                eye_drawer=RoundedModuleDrawer() if self.rounded_eyes else SquareModuleDrawer())
            
        img = img.resize((self.qr_size, self.qr_size), Image.LANCZOS)

        self.qr_image = img

    def return_qr_image(self):
        self.qr_image = self.qr_image.resize((200, 200), Image.LANCZOS)
        return self.qr_image