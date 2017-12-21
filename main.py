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

    count = len(input_files)

    for i, filename in enumerate(input_files):
        print('Processing file {} out of {}'.format(i + 1, count))
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
    # Get average value in the text rectangle
    size = font.getsize(text)
    grey = image.convert("L").load()
    average = 0

    for x in range(location[0], location[0] + size[0]):
        for y in range(location[1], location[1] + size[1]):
            average += grey[x, y]
    average /= size[0] * size[1]

    # Determine colour based on average and threshold
    if average < threshold:
        colour = (255,) * 3
    else:
        colour = (0,) * 3
    
    # Draw text
    draw = ImageDraw.Draw(image)
    draw.text(location, text, font=font, fill=colour)

    return image

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
        location = (int(config.text_x * dimension_scale), int(config.text_y * dimension_scale))
        font = ImageFont.truetype(config.font_file, int(config.font_size * dimension_scale))

        if config.text_color_mode == 0:
            image = draw_text_xor(image, text, location, font)
        elif config.text_color_mode == 1:
            image = draw_text_black_white(image, text, location, font, config.colour_threshold)
        else:
            raise NotImplementedError('Text colour mode not implemented')

    # Write the output
    image.save(output_filename)

if __name__ == "__main__":
    main(sys.argv)
