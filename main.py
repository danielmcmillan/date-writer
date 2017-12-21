#!/usr/bin/env python

import sys
import os
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageChops
from datetime import datetime
import numpy as np

import config

# Arguments: output directory, then all input files

# - get input image from system argument
# - determine font size from image height
# - determine average value in area of text rectangle, decide colour
# - draw text
# - save image

def main(args):
    """Begins processing based on given arguments"""
    if len(args) <= 2:
        print('Too few arguments.')

    output_dir = args[1]
    input_files = args[2:]

    for filename in input_files:
        process_file(filename, output_dir)

def random_filename():
    """Create a random filename with extension matching the given file name"""
    return str(uuid.uuid4())

def get_date_text(image):
    """Get date taken as a string from the given image's metadata, or None if it is not available"""
    if hasattr(image, '_getexif'):
        date_exif = image._getexif()[36867]
        if date_exif:
            date_taken = datetime.strptime(date_exif, '%Y:%m:%d %H:%M:%S')
            return date_taken.strftime(config.date_format)
    return None

def draw_text_xor(image, text, location, font):
    # Draw text on black image
    text_image = Image.new('RGB', (image.width, image.height))
    draw = ImageDraw.Draw(text_image)
    draw.text(location, text, font=font, fill=(255, 255, 255))

    # Bitwise xor text image with original image using numpy
    text_array = np.array(text_image)
    original_array = np.array(image.convert('RGB'))
    xor_array = np.bitwise_xor(text_array, original_array)

    return Image.fromarray(xor_array)

def draw_text_black_white(image, text, location, font, threshold):
    pass
    # size = font.getsize(text)
    # Average value in the text rectangle, compare to threshold

def draw_text_manual(image, text, location, font, colour):
    pass

def process_file(input_filename, output_dir):
    """Processes given file and writes output to the given directory"""
    image_name = os.path.splitext(os.path.basename(input_filename))[0]
    output_name = image_name if not config.randomise_filename else random_filename()
    output_filename = os.path.join(output_dir, '{}.{}'.format(output_name, config.output_format))

    image = Image.open(input_filename)
    dimension_scale = image.height / 1000

    # Draw text
    text = get_date_text(image)
    if text:
        location = (config.text_x * dimension_scale, config.text_y * dimension_scale)
        font = ImageFont.truetype(config.font_file, int(config.font_size * dimension_scale))

        image = draw_text_xor(image, text, location, font)

    # Write the output
    image.save(output_filename)

if __name__ == "__main__":
    main(sys.argv)
