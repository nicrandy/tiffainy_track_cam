from BlazeposeRenderer import BlazeposeRenderer
import argparse
import cv2
import time
from datetime import datetime
import os
import array
import numpy as np
import tkinter as tk

#to get screen size later
root = tk.Tk()

#change to True if you want to record the video output. Saves to same folder as this file.
record = False

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--edge', action="store_true",
                    help="Use Edge mode (postprocessing runs on the device)")
parser.add_argument('-i', '--input', type=str, default="rgb", 
                    help="'rgb' or 'rgb_laconic' or path to video/image file to use as input (default=%(default)s)")
parser.add_argument("--pd_m", type=str,
                    help="Path to an .blob file for pose detection model")
parser.add_argument("--lm_m", type=str,
                    help="Landmark model ('full' or 'lite' or '831') or path to an .blob file (default=%(default)s)")
parser.add_argument('-c', '--crop', action="store_true", 
                    help="Center crop frames to a square shape before feeding pose detection model")
parser.add_argument('--no_smoothing', action="store_true", 
                    help="Disable smoothing filter")
parser.add_argument('--filter_window_size', type=int, default=5,
                    help="Smoothing filter window size. Higher value adds to lag and to stability (default=%(default)i)")                    
parser.add_argument('--filter_velocity_scale', type=float, default=10,
                    help="Smoothing filter velocity scale. Lower value adds to lag and to stability (default=%(default)s)")                    
parser.add_argument('-f', '--internal_fps', type=int, 
                    help="Fps of internal color camera. Too high value lower NN fps (default= depends on the model)")                    
parser.add_argument('--internal_frame_height', type=int, default=640,                                                                                    
                    help="Internal color camera frame height in pixels (default=%(default)i)")                    
parser.add_argument('-s', '--stats', action="store_true", 
                    help="Print some statistics at exit")
parser.add_argument('-t', '--trace', action="store_true", 
                    help="Print some debug messages")
parser.add_argument('--force_detection', action="store_true", 
                    help="Force person detection on every frame (never use landmarks from previous frame to determine ROI)")

parser.add_argument('-3', '--show_3d', action="store_true", 
                    help="Display skeleton in 3d in a separate window (valid only for full body landmark model)")
parser.add_argument("-o","--output",
                    help="Path to output video file")
 

args = parser.parse_args()

from BlazeposeDepthaiEdge import BlazeposeDepthai

pose = BlazeposeDepthai(input_src=args.input, 
            pd_model=args.pd_m,
            lm_model=args.lm_m,
            smoothing=not args.no_smoothing,
            filter_window_size=args.filter_window_size,
            filter_velocity_scale=args.filter_velocity_scale,                
            crop=args.crop,
            internal_fps=args.internal_fps,
            internal_frame_height=args.internal_frame_height,
            force_detection=args.force_detection,
            stats=args.stats,
            trace=args.trace)   

renderer = BlazeposeRenderer(
                pose, 
                show_3d=args.show_3d, 
                output=args.output)

def draw_lines_blank_canvas(body,blank_image):
    new_size = (blank_image.shape[1]*2,blank_image.shape[0]*2)
    blank_image = cv2.resize(blank_image,new_size,interpolation = cv2.INTER_AREA)
    LINES_BODY = [[28,30,32,28,26,24,12,11,23,25,27,29,31,27], 
                [23,24],
                [22,16,18,20,16,14,12], 
                [21,15,17,19,15,13,11],
                [8,6,5,4,0,1,2,3,7],
                [10,9],
                ]
    list_connections = LINES_BODY
    lines = [np.array([body.landmarks[point,:2] for point in line]) for line in list_connections]
    cv2.polylines(blank_image, lines, False, (255, 180, 90), 2, cv2.LINE_AA)
    blank_image = cv2.resize(blank_image,(int(blank_image.shape[1]/2),int(blank_image.shape[0]/2)),interpolation = cv2.INTER_AREA)
    return blank_image

if record:
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%b_%d_%Y_%H_%M_%S")
    videoName = 'trackCam_' + timestampStr + '.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(videoName, fourcc, 15.0, (1536, 864))

while True:
    # Run blazepose on next frame
    landmarks = np.array([])
    frame0, body, landmarks = pose.next_frame()
    just_cam = frame0
    #this sends the image and landmarks to the BlazePoseRender file where our camera movement code is
    just_cam = renderer.draw(just_cam,body)

    if frame0 is None: break
    #get screen size so output window is full screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    #resize cam image
    cam_width = int(screen_width/2)
    cam_height = int(screen_height/2)
    just_cam = cv2.resize(just_cam,(cam_width,cam_height),interpolation = cv2.INTER_AREA)
    just_cam_flipped = cv2.flip(just_cam,1)
    just_cam_flipped = cv2.cvtColor(just_cam_flipped, cv2.COLOR_BGR2HSV)
    #create canvas to draw landmarks on
    blank_bottom = np.zeros((cam_height,cam_width,3), np.uint8)
    justLandmarks = blank_bottom
    if body:
        justLandmarks = draw_lines_blank_canvas(body,blank_bottom)
    justLandmarksFlipped = cv2.flip(justLandmarks,1)
    #join all of the images
    justLandmarksJoined = cv2.hconcat([justLandmarks,justLandmarksFlipped])
    just_cam_joined = cv2.hconcat([just_cam,just_cam_flipped])
    full_layout = cv2.vconcat([just_cam_joined,justLandmarksJoined])

    if record:
        out.write(full_layout)
    cv2.imshow("Yoga demo",full_layout)
    # Wait for 'q' key to stop the program 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # After we release our webcam, we also release the output
        if record:
            out.release() 
        break

cv2.destroyAllWindows()