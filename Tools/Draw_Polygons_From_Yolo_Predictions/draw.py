import argparse
from PIL import Image, ImageDraw
import os

def process_polygons(dataset_path, image_path):
    # Read all polygons from the dataset
    with open(dataset_path, "r") as f:
        polygons = f.read().splitlines()

    # Load the original image to get its size
    original_image = Image.open(image_path)
    original_width, original_height = original_image.size

    # Process polygons for lines where the first number is any integer
    for i, polygon in enumerate(polygons):
        try:
            class_index = int(polygon.split()[0])
        except ValueError:
            # Skip lines where the first part cannot be converted to an integer
            continue

        # Check if the class index is an integer
        if isinstance(class_index, int):
            points_str = polygon.split()[1:]
            # Scale the relative coordinates back to the original image size
            points = [(float(points_str[i]) * original_width, float(points_str[i + 1]) * original_height) for i in range(0, len(points_str), 2)]

            # Create an empty image with the size of the original image
            empty_image = Image.new("RGB", (original_width, original_height), color="#000000")

            # Draw the polygon on the empty image
            draw = ImageDraw.Draw(empty_image)
            draw.polygon(points, outline="#FFFFFF", fill="#FFFFFF")

            # Crop the image to fit tightly around the drawn polygon
            bbox = empty_image.getbbox()
            cropped_image = empty_image.crop(bbox)

            # Determine the target size (100xN or Nx100) based on the aspect ratio
            aspect_ratio = cropped_image.width / cropped_image.height
            if aspect_ratio >= 1:
                #target_width = min(100, cropped_image.width)
                target_width = 80
                target_height = int(target_width / aspect_ratio)
            else:
                #target_height = min(100, cropped_image.height)
                target_height = 80
                target_width = int(target_height * aspect_ratio)

            # Resize the cropped image while maintaining its aspect ratio
            resized_image = cropped_image.resize((target_width, target_height), Image.ANTIALIAS)

            # Create a new 100x100 black background
            new_image = Image.new("RGB", (100, 100), color="#000000")

            # Calculate the position to paste the resized image centered in the black background
            x_offset = (100 - target_width) // 2
            y_offset = (100 - target_height) // 2

            # Paste the resized image onto the black background
            new_image.paste(resized_image, (x_offset, y_offset))

            # Save the final image
            polygon_name = f"polygon_{i}.png"
            new_image.save(polygon_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process polygons from a dataset.")
    parser.add_argument("dataset_path", help="Path to the dataset file")
    parser.add_argument("image_path", help="Path to the original image file")
    args = parser.parse_args()

    process_polygons(args.dataset_path, args.image_path)
