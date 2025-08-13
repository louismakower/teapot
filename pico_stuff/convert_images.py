#!/usr/bin/env python3
from PIL import Image
import os

def png_to_bitmap(input_path, output_path, target_size=(64, 64)):
    """Convert PNG to 1-bit bitmap data"""
    
    # Open and resize image
    img = Image.open(input_path)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Ensure RGBA mode to handle transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Convert to 1-bit bitmap
    bitmap_data = []
    basename = os.path.splitext(os.path.basename(input_path))[0].lower()
    
    # Process row by row, then pack 8 pixels per byte
    for row in range(target_size[1]):
        for col_start in range(0, target_size[0], 8):
            byte_val = 0
            for bit in range(8):
                col = col_start + bit
                if col < target_size[0]:
                    r, g, b, a = img.getpixel((col, row))
                    
                    if basename == 'tea':
                        # Tea: non-transparent pixels should be white in bitmap
                        pixel_on = a > 128  # Non-transparent
                    elif basename == 'coffee':
                        # Coffee: dark pixels should be white in bitmap
                        grayscale = (r + g + b) // 3
                        pixel_on = grayscale < 128  # Dark pixels
                    elif basename == 'undo':
                        # Undo: dark pixels should be white, transparent should be background
                        if a < 128:  # Transparent
                            pixel_on = False
                        else:  # Non-transparent
                            grayscale = (r + g + b) // 3
                            pixel_on = grayscale < 128  # Dark pixels
                    else:
                        # Default: dark pixels are white
                        grayscale = (r + g + b) // 3
                        pixel_on = grayscale < 128
                    
                    if pixel_on:
                        byte_val |= (1 << (7 - bit))
            bitmap_data.append(byte_val)
    
    # Generate Python code for the bitmap
    with open(output_path, 'w') as f:
        basename = os.path.splitext(os.path.basename(input_path))[0]
        f.write(f"# {basename.upper()} icon bitmap (64x64)\n")
        f.write(f"{basename.upper()}_BITMAP = bytearray([\n")
        
        for i in range(0, len(bitmap_data), 16):
            line = "    "
            for j in range(16):
                if i + j < len(bitmap_data):
                    line += f"0x{bitmap_data[i + j]:02X}, "
            f.write(line + "\n")
        
        f.write("])\n")

def main():
    # Convert all images
    png_to_bitmap('tea.png', 'tea_bitmap.py')
    png_to_bitmap('coffee.png', 'coffee_bitmap.py')
    png_to_bitmap('undo.png', 'undo_bitmap.py')
    print("Converted tea.png, coffee.png, and undo.png to 64x64 bitmaps")

if __name__ == "__main__":
    main()