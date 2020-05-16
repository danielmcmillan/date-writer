#!/usr/bin/env python

import sys
import os
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageChops, ExifTags
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
        try:
            process_file(filename, output_dir)
        except Exception as err:
            print('Processing image {} ({}) failed: {}'.format(i + 1, filename, err))

def get_exif_value(image, key):
    exif = image._getexif() if hasattr(image, '_getexif') else None
    if exif is not None:
        exif_values = dict(exif)
        for exif_code, exif_key in ExifTags.TAGS.items():
            val = exif_values.get(exif_code)
            if exif_key == key and val is not None:
                return val

    return None

def random_filename(original):
    """Create a random filename with extension matching the given file name"""
    random.seed(original)
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return '{}_{}'.format(random_part, original)

def get_date_text(image):
    """Get date taken as a string from the given image's metadata, or None if it is not available"""
    date_exif = get_exif_value(image, 'DateTimeOriginal')
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

def rotate_image(image):
    orientation = get_exif_value(image, 'Orientation')
    if orientation == 3:
        return image.rotate(180, expand=True)
    elif orientation == 6:
        return image.rotate(270, expand=True)
    elif orientation == 8:
        return image.rotate(90, expand=True)
    return image

def process_file(input_filename, output_dir):
    """Processes given file and writes output to the given directory"""
    image_name = os.path.splitext(os.path.basename(input_filename))[0]
    output_name = image_name if not config.randomise_filename else random_filename(image_name)
    output_filename = os.path.join(output_dir, '{}.{}'.format(output_name, config.output_format))

    if config.skip_existing and os.path.exists(output_filename):
        return

    with Image.open(input_filename) as original:
        image = original
        if config.rotate_images:
            image = rotate_image(image)

        dimension_scale = image.height / 1000

        # Draw text
        text = get_date_text(original)
        if text:
            location = (int(config.text_x * dimension_scale), int(config.text_y * dimension_scale))
            font = ImageFont.truetype(config.font_file, int(config.font_size * dimension_scale))

            if config.text_color_mode == 0:
                image = draw_text_xor(image, text, location, font)
            elif config.text_color_mode == 1:
                image = draw_text_black_white(image, text, location, font, config.colour_threshold)
            else:
                raise NotImplementedError('Text colour mode not implemented')
        else:
            print("Warning: no date for {}".format(input_filename))

        # Write the output
        image.save(output_filename)

if __name__ == "__main__":
    main(sys.argv)
