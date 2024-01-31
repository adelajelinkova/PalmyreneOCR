import matplotlib.pyplot as plt
import numpy as np
import argparse
import os


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


def read_polygons_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    polygons = []
    for line in lines:
        parts = line.strip().split(' ')
        class_index = int(parts[0])
        coordinates = [float(coord) for coord in parts[1:]]
        polygons.append({'class_index': class_index, 'coordinates': coordinates})

    return polygons

def get_avg_polygons_size(polygons):
    polygons_heights = []
    polygons_widths = []
    for polygon in polygons:
        x_coords = [polygon['coordinates'][i] for i in range(0, len(polygon['coordinates']), 2)]
        y_coords = [polygon['coordinates'][i] for i in range(1, len(polygon['coordinates']), 2)]
        left, right, top, bottom = min(x_coords), max(x_coords), min(y_coords), max(y_coords)
        polygons_heights.append(bottom - top)
        polygons_widths.append(right - left)
    
    polygons_avg_height = np.average(polygons_heights)
    polygons_avg_width = np.average(polygons_widths)
    return (polygons_avg_height, polygons_avg_width)

def get_polygon_center(polygon):
    x_coords = [polygon['coordinates'][i] for i in range(0, len(polygon['coordinates']), 2)]
    y_coords = [polygon['coordinates'][i] for i in range(1, len(polygon['coordinates']), 2)]
    left, right, top, bottom = min(x_coords), max(x_coords), min(y_coords), max(y_coords)
    x_center = (left + right) / 2
    y_center = (top + bottom) / 2
    return (x_center, y_center)

def get_polygon_center_x(polygon):
    return get_polygon_center(polygon)[0]

def get_polygon_center_y(polygon):
    return get_polygon_center(polygon)[1]

def sort_polygons(polygons):
    """
    Sort list of all polygons in one list without reflecting rows.
    Lines are sorted from right to left.
    :param polygons: List of all unsorted polygons.
    :return: List of sorted polygons.
    """
    sorted_polygons = []
    polygons_in_rows = sort_polygons_in_rows(polygons)
    for row in polygons_in_rows:
        sorted_polygons = sorted_polygons + row
    return sorted_polygons

#output is 
def sort_polygons_in_rows(polygons):
    """
    Sort all polygons in list of rows.
    Lines are sorted from right to left.
    :param polygons: List of all unsorted polygons.
    :return: List of rows with sorted polygons.
    """
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
            #first sort row which is done by polygons center (right to left)
            rows[row_count] = sorted(rows[row_count], key=get_polygon_center_x, reverse=True)
            row_count = row_count + 1
            rows.append([])
        rows[row_count].append(polygon)
        last_polygon = polygon
    return rows

def save_sorted_polygons_to_file(sorted_polygons, output_filename):
    with open(output_filename, 'w') as file:
        for polygon in sorted_polygons:
            class_index = polygon['class_index']
            coordinates = ' '.join(map(str, polygon['coordinates']))
            file.write(f"{class_index} {coordinates}\n")

def visualize_sorted_polygons(sorted_polygons, class_names):
    # Create a colormap for unique colors for each class
    colormap = plt.cm.get_cmap('tab10', len(set(polygon['class_index'] for polygon in sorted_polygons)))

    # Set the figure size
    plt.figure(figsize=(6, 12))  # Adjust the values as needed (width, height)

    # Plot the sorted polygons
    for polygon in sorted_polygons:
        x_coords = [polygon['coordinates'][i] for i in range(0, len(polygon['coordinates']), 2)]
        y_coords = [polygon['coordinates'][i] for i in range(1, len(polygon['coordinates']), 2)]

        class_color = colormap(polygon['class_index'] % colormap.N)
        plt.fill(x_coords + [x_coords[0]], y_coords + [y_coords[0]], color=class_color, label=None)

        # Label each polygon with its class name above the polygon in 8 px font
        label_x = sum(x_coords) / len(x_coords)
        label_y = max(y_coords) + 0.02  # Adjust the label position as needed
        plt.text(label_x, label_y, f"{class_names[polygon['class_index']]}",
                 color='black', fontsize=8, ha='center', va='center')

    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.title('Sorted Polygons')
    plt.gca().invert_yaxis()  # Invert the Y-axis
    plt.savefig('Fig1.png', bbox_inches='tight')


def main(input_filename, output_filename, class_list_filename):
    class_names = read_class_names_from_file(class_list_filename)

    polygons = read_polygons_from_file(input_filename)

    print("Sorting polygons in rows...")
    sorted_polygons_rows = sort_polygons_in_rows(polygons)
    # Printing out list of sorted polygons with rows
    for index, row in enumerate(sorted_polygons_rows):
        print("Row ", index)
        for polygon in row:
            print("Polygon: ", polygon['class_index'], " - ", class_names[polygon['class_index']])
    
    print("Sorting polygons (no rows)...")
    sorted_polygons = sort_polygons(polygons)
    # Printing out list of sorted polygons without rows involved
    for polygon in sorted_polygons:
        print("Polygon: ", polygon['class_index'], " - ", class_names[polygon['class_index']])


    # Visualize and save the sorted polygons
    print("Saving visualization of polygons and sorted list to file...")
    visualize_sorted_polygons(polygons, class_names)
    print('Figure saved.')
    save_sorted_polygons_to_file(sorted_polygons, output_filename) #řadí divně, řádky bere dobře, ale v rámci řádku to má blbě   
    print('Sorted polygons saved to ', output_filename)

    print("DONE")

def generate_output_filename(input_filename):
    base_filename, ext = os.path.splitext(os.path.basename(input_filename))
    return f"{base_filename}_output.txt"

def main(args):
    input_filename = args.input
    output_filename = args.output if args.output else generate_output_filename(input_filename)
    class_list_file = "class_list.txt"

    class_names = read_class_names_from_file(class_list_file)
    polygons = read_polygons_from_file(input_filename)

    print("Sorting polygons in rows...")
    sorted_polygons_rows = sort_polygons_in_rows(polygons)
    for index, row in enumerate(sorted_polygons_rows):
        print("Row ", index)
        for polygon in row:
            print("Polygon: ", polygon['class_index'], " - ", class_names[polygon['class_index']])

    print("Sorting polygons (no rows)...")
    sorted_polygons = sort_polygons(polygons)
    for polygon in sorted_polygons:
        #print("Polygon: ", polygon['class_index'], " - ", class_names[polygon['class_index']])
        print(class_names[polygon['class_index']])

    print("Saving visualization of polygons and sorted list to file...")
    visualize_sorted_polygons(polygons, class_names)
    print('Figure saved.')
    save_sorted_polygons_to_file(sorted_polygons, output_filename)
    print(f'Sorted polygons saved to {output_filename}')

    print("DONE")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort and visualize polygons.")
    parser.add_argument("-i", "--input", help="Input filename")
    parser.add_argument("-o", "--output", help="Output filename")

    args = parser.parse_args()
    main(args)
