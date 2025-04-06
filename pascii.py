import argparse
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2

# Rich ASCII characters (high-to-low brightness)
ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def enhance_contrast(image, factor=1.5):
    """Enhance the contrast of a PIL Image."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def image_to_ascii(image_path, width=100):
    """Convert an image to ASCII characters."""
    image = Image.open(image_path)

    # Enhance contrast for better ASCII results
    image = enhance_contrast(image)

    # Maintain aspect ratio with adjustment for font proportions
    aspect_ratio = image.height / image.width
    new_height = int(width * aspect_ratio * 0.55)
    image = image.resize((width, new_height)).convert("L")  # Grayscale

    pixels = np.array(image)

    # Convert each pixel to a character
    ascii_art = [
        [ASCII_CHARS[min(int(pixel / 256 * len(ASCII_CHARS)), len(ASCII_CHARS) - 1)] for pixel in row]
        for row in pixels
    ]

    return ascii_art, new_height, aspect_ratio

def save_ascii_to_image(ascii_art, image_path, width, height, aspect_ratio, font_size=20, output_format="png"):
    """Save ASCII art as an image (PNG)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "ASCII_Img")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    image_name = os.path.splitext(os.path.basename(image_path))[0]
    save_path = os.path.join(save_dir, f"{image_name}.{output_format}")

    # Load image for color mapping
    image = cv2.imread(image_path)
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    # Font metrics
    char_width = font_size * 0.65
    char_height = font_size * 1.5

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Output image size
    img_width = int(width * char_width)
    img_height = int(height * char_height)

    # Create canvas
    output_image = Image.new("RGB", (img_width, img_height), color="black")
    draw = ImageDraw.Draw(output_image)

    # Draw ASCII characters
    y_offset = 0
    for y, row in enumerate(ascii_art):
        x_offset = 0
        for x, char in enumerate(row):
            b, g, r = image[y, x]
            draw.text((x_offset, y_offset), char, font=font, fill=(r, g, b))
            x_offset += char_width
        y_offset += char_height

    # Optional upscale for better visual fidelity
    upscale_factor = 2
    output_image = output_image.resize(
        (img_width * upscale_factor, img_height * upscale_factor),
        Image.Resampling.LANCZOS
    )

    output_image.save(save_path)
    print(f"\nASCII image saved as {output_format.upper()} at: {save_path}")

def find_images(folder="images"):
    """Search for images in a given folder and return a list."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, folder)

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        return []

    return [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert images to ASCII art.")
    parser.add_argument("Images", nargs="?", help="Path to input image (leave empty to auto-detect)")
    parser.add_argument("-w", "--width", type=int, default=100, help="ASCII art width")

    args = parser.parse_args()

    # If image not provided, auto-detect from /images
    if args.Images is None:
        images = find_images()
        if not images:
            print("No images found in 'images/' folder. Please provide an image manually.")
            exit(1)

        print("\nAvailable images:")
        for idx, img in enumerate(images, 1):
            print(f"{idx}. {img}")

        choice = input("\nSelect the image (or type path manually): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(images):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            args.Images = os.path.join(script_dir, "images", images[int(choice) - 1])
        else:
            args.Images = choice

    # Convert and save
    ascii_art, height, aspect_ratio = image_to_ascii(args.Images, args.width)
    save_ascii_to_image(ascii_art, args.Images, args.width, height, aspect_ratio, font_size=20, output_format="png")