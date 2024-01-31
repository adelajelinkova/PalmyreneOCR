from tensorflow.keras.models import load_model
from tensorflow.keras.models import model_from_json
import numpy as np
import cv2
import tensorflow as tf
import os
import argparse
from PIL import Image

# Only allocates a subset of the available GPU Memory and take more as needed.
# Prevents "Failed to get convolution algorithm" error on Elementary OS Juno.
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(config=config)

# Argument parser
ap = argparse.ArgumentParser()
ap.add_argument("--imdir", "-d", type=str, required=True, help="Path to directory containing images to predict.")
ap.add_argument("--classes", "-c", type=str, required=True, help="Path to dictionary containing classes in alphabetical order.")
ap.add_argument("--imsize", "-s", type=int, default=28, help="Size of input images.")
ap.add_argument("--archpath", "-a", type=str, required=True, default="./model.json", help="Path to model architecture in .json format.")
ap.add_argument("--weipath", "-w", type=str, required=True, default="./model.h5", help="Path to model weights in .h5 format.")
args = vars(ap.parse_args())

# Load the model architecture and weights
architecture = args["archpath"]
weights = args["weipath"]
json_file = open(architecture, 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights(weights)

# Open Class labels dictionary
classes_dict = eval(open(args["classes"], 'r').read())
class_names = list(classes_dict.values())

# Get a list of image files in the specified directory
image_dir = args["imdir"]
image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

# Counter for misclassified files
misclassified_files = 0

# Iterate through the image files and make predictions
for image_file in image_files:
    # Load and preprocess the image
    img_path = os.path.join(image_dir, image_file)
    img = Image.open(img_path)
    img = img.resize((args["imsize"], args["imsize"]), Image.BILINEAR)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = np.array(img)
    img = img.reshape((1, img.shape[0], img.shape[1], 1))
    img = img.astype('float32') / 255

    # Make predictions on the image
    preds = loaded_model.predict(img)
    predicted_class_idx = np.argmax(preds)
    predicted_class_name = class_names[predicted_class_idx]
    
    # Extract the folder name from the image file's parent directory
    folder_name = os.path.basename(os.path.dirname(img_path))

    # Check if the folder name matches the predicted class name
    #if folder_name != predicted_class_name:
    #    misclassified_files += 1

    certainty = preds[0][predicted_class_idx]

    # Print the results for each image
    #print(f"Image: {image_file}, Predicted Class: {predicted_class_name}, Folder Name: {folder_name}, Certainty: {certainty:.4f}")
    print({image_file}, " : " , {predicted_class_name})
# Print the count of misclassified files
#print(f"Total misclassified files: {misclassified_files}")