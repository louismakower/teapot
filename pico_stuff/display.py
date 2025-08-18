"""
Display functions using the updated GC9A01 driver
Replaces display.py functionality with new driver interface
"""

from machine import Pin, SPI
import time
import driver
import tea_bitmap
import coffee_bitmap
import undo_bitmap
import vga2_8x8 as font_8pt
import vga2_16x16 as font_16pt

# Color definitions
TEA = 0xC428
DARK_TEA = 0x8AE5
COFFEE = 0xbc48
DARK_COFFEE = 0x69A0
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xf800

class Display:
    def __init__(self, spi, dc, cs, reset, backlight):
        """Initialize the display with the new driver"""
        self.display = driver.GC9A01(
            spi=spi,
            dc=dc,
            cs=cs,
            reset=reset,
            backlight=backlight,
            rotation=0
        )
        self.width = 240
        self.height = 240
    
    def draw_text_centred(self, y, text, color, bg_color=None, font_size=8):
        """Draw text centered horizontally at the given y position"""
        if font_size <= 8:
            font = font_8pt
        else:
            font = font_16pt
        
        # Calculate text width for centering
        text_width = len(text) * font.WIDTH
        x = (self.width - text_width) // 2
        
        if bg_color is not None:
            self.display.text(font, text, x, y, color, bg_color)
        else:
            self.display.text(font, text, x, y, color)
    
    def draw_instruction_box(self, messages, color=WHITE):
        """Draw a status message in a box at the bottom of the screen"""
        # Status box parameters
        box_height = 62
        box_y = self.height - box_height
        text_y = box_y + 12  # Center text vertically in box
        
        # Clear the status area and draw border
        # self.display.fill_rect(0, box_y, self.width, box_height, BLACK)
        self.display.line(0, box_y, self.width, box_y, WHITE)
        
        # Draw centered text
        for i, message in enumerate(messages):
            self.draw_text_centred(text_y + 10*i, message, color, font_size=8)
    
    def draw_bitmap(self, x, y, bitmap_module, color=None):
        """Draw a bitmap using the new driver's bitmap method"""
        # If color is specified, create a custom palette
        if color is not None:
            # Create a temporary copy of the bitmap module with custom colors
            class CustomBitmap:
                HEIGHT = bitmap_module.HEIGHT
                WIDTH = bitmap_module.WIDTH
                BPP = bitmap_module.BPP
                PALETTE = [BLACK, color]  # Background black, foreground custom color
                BITMAP = bitmap_module.BITMAP
            
            self.display.bitmap(CustomBitmap(), x, y)
        else:
            self.display.bitmap(bitmap_module, x, y)
    
    def draw_tea_registered(self):
        """Display tea registered message with bitmap"""
        self.display.fill(BLACK)
        
        # Calculate centered position for 64x64 bitmap
        x = (self.width - 64) // 2
        y = ((self.height - 64) // 2) - 20
        
        # Draw tea bitmap with tea color
        self.draw_bitmap(x, y - 10, tea_bitmap, WHITE)
        
        # Draw text below bitmap
        self.draw_text_centred(y + 10 + 64, "TEA REGISTERED", DARK_TEA, font_size=16)
        time.sleep(2)
    
    def draw_coffee_registered(self):
        """Display coffee registered message with bitmap"""
        self.display.fill(BLACK)
        
        # Calculate centered position for 64x64 bitmap
        x = (self.width - 64) // 2
        y = ((self.height - 64) // 2) - 20
        
        # Draw coffee bitmap with coffee color
        self.draw_bitmap(x, y - 10, coffee_bitmap, WHITE)
        
        # Draw text below bitmap
        self.draw_text_centred(y + 64, "COFFEE", COFFEE, font_size=16)
        self.draw_text_centred(y + 20 + 64, "REGISTERED", COFFEE, font_size=16)
        time.sleep(2)
    
    def draw_undo(self):
        """Display undo message with bitmap"""
        self.display.fill(BLACK)
        
        # Calculate centered position for 64x64 bitmap
        x = (self.width - 64) // 2
        y = ((self.height - 64) // 2) - 20
        
        # Draw undo bitmap in white
        self.draw_bitmap(x, y - 10, undo_bitmap, WHITE)
        
        # Draw text below bitmap
        self.draw_text_centred(y + 64, "UNDONE", WHITE, font_size=16)
        self.draw_text_centred(y + 20 + 64, "LAST DRINK", WHITE, font_size=16)
        time.sleep(2)
    
    def home_screen(self, username, teas, coffees):
        """Display the home screen with drink counts and idle status"""
        self.display.fill(BLACK)
        
        # Format username possessive correctly
        if username[-1] not in "sS":
            line1 = f"{capitalise(username)}'s Drinks"
        else:
            line1 = f"{capitalise(username)}' Drinks"
        
        line2 = f"Teas drunk: {teas}"
        line3 = f"Coffees drunk: {coffees}"
        
        # Draw text lines centered
        self.draw_text_centred(67, line1, WHITE, font_size=8)
        self.draw_text_centred(97, line2, WHITE, font_size=8)
        self.draw_text_centred(127, line3, WHITE, font_size=8)
        
        # Draw instructions message at bottom
        self.draw_instruction_box(["Tap for tea", "Double tap for coffee", "Hold for undo"])

    
    def undo_failed(self):
        """Display undo failed message"""
        self.display.fill(BLACK)
        self.draw_text_centred(120, "UNDO NOT POSSIBLE", WHITE, font_size=8)
        self.draw_text_centred(130, "TOO LONG SINCE LAST DRINK", WHITE, font_size=8)
        time.sleep(2)
    
    def welcome(self, username):
        """Display welcome message"""
        self.display.fill(BLACK)
        self.draw_text_centred(110, f"Welcome", WHITE, font_size=16)
        self.draw_text_centred(130, f"{capitalise(username)}!", WHITE, font_size=16)
        time.sleep(3)

    def status(self, message):
        """Display status message at the top of the screen"""
        self.draw_text_centred(22, message, RED, font_size=8)

    def error_message(self, message):
        self.display.fill(BLACK)
        lines = []
        words = message.split(" ")
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed 20 characters
            if len(current_line + " " + word) <= 20:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                # Current line is full, start a new one
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        # Don't forget the last line
        if current_line:
            lines.append(current_line)
        
        # Calculate starting Y position to center vertically
        line_height = 9
        total_height = len(lines) * line_height
        start_y = (self.height - total_height) // 2
        
        # Draw each line centered
        for i, line in enumerate(lines):
            y_pos = start_y + i * line_height
            self.draw_text_centred(y_pos, line, WHITE)

def capitalise(self):
    return self[0].upper() + self[1:]

# Example usage and test code
if __name__ == "__main__":
    # Initialize SPI and display
    spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(11))
    display = Display(
        spi=spi,
        dc=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT), 
        reset=Pin(6, Pin.OUT),
        backlight=Pin(0, Pin.OUT)
    )
    
    # Test all functions
    # display.welcome("louis")
    # display.draw_tea_registered()
    # display.draw_coffee_registered()
    # display.draw_undo()
    # display.undo_failed()
    display.home_screen("louis", 10, 10)