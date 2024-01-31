import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import json

def read_class_names_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    class_names = {}
    for line in lines:
        parts = line.strip().split(':')
        class_index = int(parts[0])
        class_name = parts[1].strip().strip('"')
        class_names[class_index] = class_name

    return class_names

def read_polygons_from_json(json_data):
    predictions = json_data["predictions"]
    polygons = []
    for prediction in predictions:
        class_index = prediction["class_id"]
        coordinates = [(point["x"], point["y"]) for point in prediction["points"]]
        polygons.append({'class_index': class_index, 'coordinates': coordinates})

    return polygons

def get_avg_polygons_size(polygons):
    polygons_heights = []
    polygons_widths = []
    for polygon in polygons:
        x_coords = [point[0] for point in polygon['coordinates']]
        y_coords = [point[1] for point in polygon['coordinates']]
        left, right, top, bottom = min(x_coords), max(x_coords), min(y_coords), max(y_coords)
        polygons_heights.append(bottom - top)
        polygons_widths.append(right - left)
    
    polygons_avg_height = np.average(polygons_heights)
    polygons_avg_width = np.average(polygons_widths)
    return (polygons_avg_height, polygons_avg_width)

def get_polygon_center(polygon):
    x_coords = [point[0] for point in polygon['coordinates']]
    y_coords = [point[1] for point in polygon['coordinates']]
    left, right, top, bottom = min(x_coords), max(x_coords), min(y_coords), max(y_coords)
    x_center = (left + right) / 2
    y_center = (top + bottom) / 2
    return (x_center, y_center)

def get_polygon_center_x(polygon):
    return get_polygon_center(polygon)[0]

def get_polygon_center_y(polygon):
    return get_polygon_center(polygon)[1]

def sort_polygons(polygons):
    sorted_polygons = []
    polygons_in_rows = sort_polygons_in_rows(polygons)
    for row in polygons_in_rows:
        sorted_polygons = sorted_polygons + row
    return sorted_polygons

def sort_polygons_in_rows(polygons):
    rows = []
    avg_height, avg_width = get_avg_polygons_size(polygons)
    threshold_height = avg_height / 2
    first_sorted_polygons = sorted(polygons, key=get_polygon_center_y)
    row_count = 0
    last_polygon = first_sorted_polygons[0]
    rows.append([])
    for polygon in first_sorted_polygons:
        compare_value = abs(get_polygon_center_y(polygon) - get_polygon_center_y(last_polygon))
        if compare_value > threshold_height:
            rows[row_count] = sorted(rows[row_count], key=get_polygon_center_x, reverse=True)
            row_count = row_count + 1
            rows.append([])
        rows[row_count].append(polygon)
        last_polygon = polygon
    return rows

def visualize_sorted_polygons(sorted_polygons, class_names):
    colormap = plt.cm.get_cmap('tab10', len(set(polygon['class_index'] for polygon in sorted_polygons)))
    plt.figure(figsize=(6, 12))
    for polygon in sorted_polygons:
        x_coords = [point[0] for point in polygon['coordinates']]
        y_coords = [point[1] for point in polygon['coordinates']]
        class_color = colormap(polygon['class_index'] % colormap.N)
        plt.fill(x_coords + [x_coords[0]], y_coords + [y_coords[0]], color=class_color, label=None)
        label_x = sum(x_coords) / len(x_coords)
        label_y = max(y_coords) + 0.02
        plt.text(label_x, label_y, f"{class_names[polygon['class_index']]}",
                 color='black', fontsize=8, ha='center', va='center')
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.title('Sorted Polygons')
    plt.gca().invert_yaxis()
    plt.savefig('Fig1.png', bbox_inches='tight')

def save_sorted_polygons_to_json(sorted_polygons, input_filename, class_names):
    output_filename = os.path.splitext(input_filename)[0] + "-sorted.json"
    output_data = {"predictions": []}
    for polygon in sorted_polygons:
        class_index = polygon['class_index']
        coordinates = [{"x": point[0], "y": point[1]} for point in polygon['coordinates']]
        output_data["predictions"].append({"class_id": class_index, "points": coordinates})

    with open(output_filename, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    return output_filename

def main(args):
    input_filename = args.input
    class_list_file = "class_list.txt"

    class_names = read_class_names_from_file(class_list_file)

    with open(input_filename, 'r') as json_file:
        json_data = json.load(json_file)

    polygons = read_polygons_from_json(json_data)

    sorted_polygons_rows = sort_polygons_in_rows(polygons)
    for index, row in enumerate(sorted_polygons_rows):
        print("Row ", index)
        for polygon in row:
            print("Polygon: ", polygon['class_index'], " - ", class_names[polygon['class_index']])

    sorted_polygons = sort_polygons(polygons)
    for polygon in sorted_polygons:
        print(class_names[polygon['class_index']])

    visualize_sorted_polygons(polygons, class_names)
    print('Figure saved.')

    output_filename = save_sorted_polygons_to_json(sorted_polygons, input_filename, class_names)
    print(f'Sorted polygons saved to: {output_filename}')

    print("DONE")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort and visualize polygons.")
    parser.add_argument("-i", "--input", help="Input filename")
    args = parser.parse_args()
    main(args)
