#!/usr/bin/env python

import sys
import os
import uuid

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

def random_filename(filename):
    """Create a random filename with extension matching the given file name"""
    extension = os.path.splitext(filename)[-1]
    return str(uuid.uuid4()) + extension

def process_file(input_filename, output_dir):
    """Processes given file and writes output to the given directory"""
    input_name = os.path.split(input_filename)[-1]
    output_name = input_name if not config.randomise_filename else random_filename(input_name)
    output_filename = os.path.join(output_dir, output_name)

    print("Input: {}, output: {}".format(input_filename, output_filename))

if __name__ == "__main__":
    main(sys.argv)
