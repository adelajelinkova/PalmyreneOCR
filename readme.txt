Palmyrene Characters Instance Segmentation toolset
Intelectual property of the Czech University of Life Sciences in Prague
(c) Adéla Hamplová, (c) David Franc
YOLO training and prediction notebooks originally designed by (c) ultralytics, edited by Adéla Hamplová
***** READ ME *****
A) For multi-class instance segmentation follow steps 1-2.
B) For single-class segmentation, follow steps 1-5.

1) Get predictions by predicting with YOLO or Roboflow pre-trained model.
2) Sort predictions using either sort.py for YOLO or sort_json.py for Roboflow predictions and get the plots and transcripts.
3) If the sorted polygons are in .json format, use the json_to_polygon tool to convert them to yolo format.
4) Use the draw.py tool to create a folder containing letters in 100x100 images in the correct order for classificaiton.
5) Use predict_polygons.py to get the transcript using the pre-trained classifier.