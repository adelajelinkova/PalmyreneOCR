import json
import argparse
from PIL import Image

def convert_to_relative_coordinates(points, image_width, image_height):
    # Convert points to relative coordinates with 6 decimals
    relative_points = [(round(point["x"] / image_width, 6), round(point["y"] / image_height, 6)) for point in points]
    return relative_points

def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size  # returns (width, height)

def save_yolo_format(json_data, image_width, image_height, output_filename):
    predictions = json_data["predictions"]
    with open(output_filename, 'w') as output_file:
        for prediction in predictions:
            class_id = prediction["class_id"]
            points = prediction["points"]

            # Convert points to relative coordinates
            relative_points = convert_to_relative_coordinates(points, image_width, image_height)

            # Instance segmentation format: class_id x1 y1 x2 y2 x3 y3 ...
            instance_segmentation = f"{class_id} {' '.join([f'{point[0]:.6f} {point[1]:.6f}' for point in relative_points])}"
            output_file.write(instance_segmentation + '\n')

def main():
    parser = argparse.ArgumentParser(description="Save instance segmentation data in the specified format to a file.")
    parser.add_argument("--json_data", "-j", type=str, help="Path to the JSON data file")
    parser.add_argument("--image_path", "-i", type=str, help="Path to the image file")

    args = parser.parse_args()

    # Load JSON data
    with open(args.json_data, "r") as json_file:
        json_data = json.load(json_file)

    # Get image size
    image_width, image_height = get_image_size(args.image_path)

    # Prepare output file name
    json_name = args.json_data.split('/')[-1].split('.')[0]
    output_file_name = f"{json_name}-yolo-formatted.txt"

    # Save YOLO format to a file
    save_yolo_format(json_data, image_width, image_height, output_file_name)

    print(f"YOLO format saved to: {output_file_name}")

if __name__ == "__main__":
    main()
