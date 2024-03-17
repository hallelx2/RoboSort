import os
# import math
import numpy as np
import cv2
from tensorflow.lite.python.interpreter import Interpreter
import threading
import time
from RobotArm import *
import pyttsx3

# -engine = pyttsx3.init()


class VideoStream:
    """Camera object that controls video streaming from the Picamera"""

    def __init__(self, resolution=(1280, 720), framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True


model_name = 'custom_model_lite'
graph_name = 'detect (4).tflite'
label_path = 'trash_label_map.txt'
confidence = 0.5

imW, imH = 1280, 720

CWD_PATH = os.getcwd()

PATH_TO_CKPT = os.path.join(CWD_PATH, model_name, graph_name)
PATH_TO_LABELS = os.path.join(CWD_PATH, model_name, label_path)

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

if labels[0] == '???':
    del labels[0]

interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

# get model details

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
float_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Check if your model was made with TF1 or TF2 because output format differs
output_name = output_details[0]['name']

if 'StatefulPartitionedCall' in output_name:
    box_index, class_index, score_index = 1, 3, 0
else:
    box_index, class_index, score_index = 0, 1, 2

# initialize the frame rate calculation
frequency = cv2.getTickFrequency()
frame_rate = 1

# initialize the video stream

video_stream = VideoStream(resolution=(imW, imH), framerate=30).start()
time.sleep(1)

while True:
    # Grab the video
    t1 = cv2.getTickFrequency()
    frame1 = video_stream.read()

    # make a copy and work on it
    frame = frame1.copy()
    frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resized_frame = cv2.resize(frame_RGB, (width, height))
    input_data = np.expand_dims(resized_frame, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if float_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the detection on the given frame of mage from the video
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[box_index]['index'])[0]  # class index coordinates of detected
    # objects
    classes = interpreter.get_tensor(output_details[class_index]['index'])[0]  # confidence of detected objects
    scores = interpreter.get_tensor(output_details[score_index]['index'])[0]  # boxes of detected objects

    # cv2.circle(frame, (275, 445), 390, (0, 0, 255), 3, 8, 0)
    # cv2.circle(frame, (275, 445), 365, (0, 0, 255), 3, 8, 0)
    # cv2.circle(frame, (275, 445), 340, (0, 0, 255), 3, 8, 0)
    # cv2.circle(frame, (275, 445), 315, (0, 0, 255), 3, 8, 0)
    # cv2.circle(frame, (275, 445), 290, (0, 0, 255), 3, 8, 0)

    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if (scores[i] > confidence) and (scores[i] <= 1.0):
            # Get bounding box coordinates and draw box Interpreter can return coordinates that are outside of image
            # dimensions, need to force them to be within image using max() and min()
            startY = int(max(1, (boxes[i][0] * height)))
            startX = int(max(1, (boxes[i][1] * width)))
            endY = int(min(imH, (boxes[i][2] * height)))
            endX = int(min(imW, (boxes[i][3] * width)))

            centerX = (endX - startX) // 2
            centerY = (endY - startY) // 2

            origin = centerX, centerY

            cv2.rectangle(frame, (startX, startY), (endX, endY), (10, 255, 0), 2)

            cv2.circle(frame, (275, 445), 390, (0, 0, 255), 3, 8, 0)
            cv2.circle(frame, (275, 445), 365, (0, 0, 255), 3, 8, 0)
            cv2.circle(frame, (275, 445), 340, (0, 0, 255), 3, 8, 0)
            cv2.circle(frame, (275, 445), 315, (0, 0, 255), 3, 8, 0)
            cv2.circle(frame, (275, 445), 290, (0, 0, 255), 3, 8, 0)

            # Draw label
            object_name: str = labels[int(classes[i])]  # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i] * 100))  # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Get font size
            label_ymin = max(startY, labelSize[1] + 10)  # Make sure not to draw label too close to top of window

            cv2.rectangle(frame, (startX, label_ymin - labelSize[1] - 10),
                          (startX + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255),
                          cv2.FILLED)  # Draw white box to put label text in
            cv2.putText(frame, label, (startX, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),
                        2)  # Draw label text
            # engine.say(object_name)

    # Calculate the frame rate
    # time = (time.time() - t1)
    # frame_rate = 1 / time

    cv2.putText(frame, 'FPS: {0:.2f}'.format(frame_rate), (30, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 101, 40), 3, cv2.LINE_AA)

    # Draw all results so that they can be seen on the frame

    cv2.imshow('Waste Detector', frame)

    # Calculate the frame rate
    t2 = cv2.getTickCount()
    time = (t2 - t1) / frequency
    frame_rate = 1 / time

    # Quit the whole loop
    if cv2.waitKey(1) == ord('q'):
        break

# engine.runAndWait()
cv2.destroyAllWindows()
video_stream.stop()
