"""
pyFCCG: python Feedback Controlled Crystal Growth
"""

# modules
import cv2
import slackweb
import os
import time
from scipy import signal
import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import nbformat
import matplotlib.pyplot as plt
import sys

####Functions####
def img_to_video(fps, out_file, img_dir):
    # Create a list of image files
    img_list = sorted(os.listdir(img_dir))

    # Get the size of the images
    img_size = cv2.imread(os.path.join(img_dir, img_list[0])).shape[:2]

    # Create an object to save the video
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(out_file, fourcc, fps, img_size)

    # Read in the images and write them to the video
    for img_name in img_list:
        img_path = os.path.join(img_dir, img_name)
        img = cv2.imread(img_path)
        out.write(img)
    # Save the video and release the object
    out.release()


def int_ask(question):
    while True:
        A = input(question)
        if A == "0" or A == "1":
            break
        else:
            pass
    A = int(A)
    return A


def save_img(save_path, img, ela_time, putText):
    img_c = img.copy()
    img_size = img_c.shape[:2]
    ww, hh = img_size[1], img_size[0]
    if putText:
        cv2.putText(
            img_c,
            ela_time,
            org=(800, 1050),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA,
        )
    img_c = img_c[0 : int(hh), int(ww / 2 - hh / 2) : int(ww / 2 + hh / 2)]
    cv2.imwrite(save_path, img_c)


def elapsed_time_text(time_):
    elapsed_time = int(time.monotonic() - time_)
    elapsed_hour = elapsed_time // 3600
    elapsed_minute = (elapsed_time % 3600) // 60
    elapsed_second = elapsed_time % 3600 % 60
    ela_time = (
        str(elapsed_hour).zfill(2)
        + "h "
        + str(elapsed_minute).zfill(2)
        + "m "
        + str(elapsed_second).zfill(2)
        + "s"
    )
    return ela_time


def get_time(hms, start_time):
    time_ = int(time.monotonic() - start_time)
    if hms == "hour":
        time_ = float("%0.6f" % (time_ / 3600))
    if hms == "minute":
        time_ = float("%0.3f" % (time_ / 60))
    if hms == "second":
        time_ = float("%0.1f" % (time_))
    else:
        pass
    return time_


# for data smoothing
def SGs(y, dn, poly):
    # y as np.array, dn as int, poly as int
    n = len(y) // dn
    if n % 2 == 0:
        N = n + 1
    elif n % 2 == 1:
        N = n
    else:
        print("window length can't set as odd")
    SGsmoothed = signal.savgol_filter(y, window_length=N, polyorder=poly)
    return SGsmoothed
    
def print_camera_properties(cap):
    # Define a dictionary of property IDs and their names
    property_names = {
        cv2.CAP_PROP_POS_MSEC: "CAP_PROP_POS_MSEC",
        cv2.CAP_PROP_POS_FRAMES: "CAP_PROP_POS_FRAMES",
        cv2.CAP_PROP_POS_AVI_RATIO: "CAP_PROP_POS_AVI_RATIO",
        cv2.CAP_PROP_FRAME_WIDTH: "CAP_PROP_FRAME_WIDTH",
        cv2.CAP_PROP_FRAME_HEIGHT: "CAP_PROP_FRAME_HEIGHT",
        cv2.CAP_PROP_MODE: "CAP_PROP_MODE",
        cv2.CAP_PROP_BRIGHTNESS: "CAP_PROP_BRIGHTNESS",
        cv2.CAP_PROP_CONTRAST: "CAP_PROP_CONTRAST",
        cv2.CAP_PROP_SATURATION: "CAP_PROP_SATURATION",
        cv2.CAP_PROP_HUE: "CAP_PROP_HUE",
        cv2.CAP_PROP_GAIN: "CAP_PROP_GAIN",
        cv2.CAP_PROP_EXPOSURE: "CAP_PROP_EXPOSURE",
        cv2.CAP_PROP_WB_TEMPERATURE: "CAP_PROP_WB_TEMPERATURE",
        cv2.CAP_PROP_GAMMA: "CAP_PROP_GAMMA",
        cv2.CAP_PROP_FOCUS: "CAP_PROP_FOCUS",
        cv2.CAP_PROP_TEMPERATURE: "CAP_PROP_TEMPERATURE",
        cv2.CAP_PROP_AUTO_EXPOSURE: "CAP_PROP_AUTO_EXPOSURE",
        cv2.CAP_PROP_AUTOFOCUS: "CAP_PROP_AUTOFOCUS",
        cv2.CAP_PROP_AUTO_WB: "CAP_PROP_AUTO_WB",
        cv2.CAP_PROP_FOURCC: "CAP_PROP_FOURCC"
        # Add more properties as needed
    }

    # Get and display camera properties
    for prop_id, prop_name in property_names.items():
        prop_value = cap.get(prop_id)
        print(f"{prop_name}: {prop_value}")

def crop_to_square(image):
    # image resize to square
    height, width, _ = image.shape

    # Get the smaller of the width and height
    min_dim = min(height, width)

    # Define a square region and crop
    crop_x = (width - min_dim) // 2
    crop_y = (height - min_dim) // 2
    cropped_image = image[crop_y:crop_y + min_dim, crop_x:crop_x + min_dim]
    
    return cropped_image

def check_camera_port():
    true_ID = []        
    camera_ID_check = [0,1,2,3,4]

    for camera_ID in camera_ID_check:
        cap = cv2.VideoCapture(camera_ID, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        ret, frame = cap.read()

        if ret is True:
            print(f"\nport number {camera_ID} Find!")
            true_ID.append(camera_ID)

            # Abandon the first too bright images
            for i in range(3):
                ret, frame = cap.read()
                time.sleep(0.1)

            # BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # image resize to square
            cropped_image = crop_to_square(image)

            # img_check
            plt.imshow(cropped_image)
            plt.axis('off')
            plt.show()

        else:
            print(f"\nport number {camera_ID} is not available")

        cap.release()

    if len(true_ID) == 0:
        print("Failed to detect a camera. Check the cable connections")
        sys.exit(0)

    while True:
        ID = input('\nInput Port Number that You Use. Input Q to quit.\n')
        if ID == 'Q':
            sys.exit(0)
        else:
            try:
                ID = int(ID)
                if not ID in true_ID:
                    print('It is not available. Use different Port Number')
                if ID in true_ID:
                    break
            except:
                print('Invalid input')

    camera_ID = ID + cv2.CAP_DSHOW
    return camera_ID

def img_check(camera_ID, camera_settings, r):
    cap = cv2.VideoCapture(camera_ID)
    
    # print('The default camera setting is...')
    # print_camera_properties(cap)
    
    for prop_id, prop_value in camera_settings.items():
        cap.set(prop_id, prop_value)

    # print('Now the camera setting is...')
    # print_camera_properties(cap)

    print("\nCheck your camera view. Press 'q' to quit. \n")    

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, image = cap.read()
        
        # image resize to square
        image = crop_to_square(image)
        
        # Draw lines
        hh, ww, _ = image.shape
        image = cv2.line(image, (0, int(ww/2)),(int(hh), int(ww/2)), (0, 0, 0), 2, lineType=cv2.LINE_8, shift=0) 
        image = cv2.line(image, (int(hh/2), 0),(int(hh/2), int(ww)), (0, 0, 0), 2, lineType=cv2.LINE_8, shift=0)
        
        radius = [r, 565]
        color = [(200,0,0),(0,200,0)]
        text = ['Dish', 'Hotplate']
        for k in range(len(radius)):
            image = cv2.circle(image, (int(hh/2), int(ww/2)),radius[k],color[k],2,lineType=cv2.LINE_4,shift=0)
            cv2.putText(image, text[k], (int(hh/2), int(ww/2) + radius[k]-50), font, 1, color[k], 2, lineType = cv2.LINE_AA)

        cv2.putText(image, "Press Q to quit", (50, 50), font, 1, (0,0,0), 2, lineType = cv2.LINE_AA)
        
        windowname = f'Camera ID: {camera_ID}'
        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowname, 800, 800) 
        cv2.imshow(windowname, image)

        time.sleep(0.1)

        if cv2.waitKey(20) & 0xFF == ord('q'):
            print('Check is done')
            break

    # When everything done, release the capture
    cv2.destroyAllWindows()
    return cap

def save_code(ipynb_file_path, text_file_path):
    # Read .ipynb file
    with open(ipynb_file_path, "r", encoding="utf-8") as ipynb_file:
        nb_content = ipynb_file.read()

    # analyze the content by using nbformat
    notebook = nbformat.reads(nb_content, as_version=4)

    # save the content in a txt file
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        for cell in notebook.cells:
            if cell.cell_type == "code":
                text_file.write(f"## Code Cell ##\n{cell.source}\n\n")
            elif cell.cell_type == "markdown":
                text_file.write(f"## Markdown Cell ##\n{cell.source}\n\n")
