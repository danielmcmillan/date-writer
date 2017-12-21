"""Configuration for date-writer"""

# Dimension to specify measurements relative to (0 for width, 1 for height)
relative_dimension = 1

# Output file format
output_format = 'jpg'

# Whether to randomise the output filename
randomise_filename = True

##
# Date text
##

# Location of date text, specified as thousandths of the reference dimension
text_x = 20
text_y = 15

# Truetype font file
font_file = 'font.ttf'

# Font size, specified as thousandths of the reference dimension
font_size = 60

# Format for date
date_format = '%B %-d, %Y'

# Text colour mode (0 for bitwise xor, 1 for automatic black/white, 2 for manual colour)
text_color_mode = 1

# Brightness threshold for automatic black/white text colour mode
colour_threshold = 128

# Text colour for manual text colour mode
text_colour = (255, 255, 255)
