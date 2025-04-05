from PIL import Image, ImageDraw, ImageFont
import os

# Create a 300x400 image with a light gray background
img = Image.new('RGB', (300, 400), color='#f0f0f0')
draw = ImageDraw.Draw(img)

# Add some text
try:
    font = ImageFont.truetype("arial.ttf", 24)
except IOError:
    font = ImageFont.load_default()

text = "Story Cover"
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Center the text
x = (300 - text_width) // 2
y = (400 - text_height) // 2

draw.text((x, y), text, fill='#666666', font=font)

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)

# Save the image
img.save('static/placeholder.jpg')
