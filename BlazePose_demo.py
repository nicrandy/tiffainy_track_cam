#!/usr/bin/env python3

from BlazeposeRenderer import BlazeposeRenderer
import argparse
import cv2
from sklearn import svm
import pickle
import time
import os
from random import sample
import array
import numpy as np
import servo_tracker as tracker
import tkinter as tk

#to get screen size later
root = tk.Tk()

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


LINES_BODY = [[9,10],[4,6],[1,3],
                    [12,14],[14,16],[16,20],[20,18],[18,16],
                    [12,11],[11,23],[23,24],[24,12],
                    [11,13],[13,15],[15,19],[19,17],[17,15],
                    [24,26],[26,28],[32,30],
                    [23,25],[25,27],[29,31]]
def draw_lines_blank_canvas(body,blank_image):
    LINES_BODY = [[28,30,32,28,26,24,12,11,23,25,27,29,31,27], 
                [23,24],
                [22,16,18,20,16,14,12], 
                [21,15,17,19,15,13,11],
                [8,6,5,4,0,1,2,3,7],
                [10,9],
                ]
    list_connections = LINES_BODY
    lines = [np.array([body.landmarks[point,:2] for point in line]) for line in list_connections]
    print("Demo render lines:", lines)
    cv2.polylines(blank_image, lines, False, (255, 180, 90), 2, cv2.LINE_AA)
    return blank_image



currentCamAngle = 90
def rotate_cam(landmarks):
    global currentCamAngle
    xMin = 1000
    xMax = -1000
    for landmark in landmarks:
        x,y,z = landmark
        if x > xMax:
            xMax = x 
        if x < xMin:
            xMin = x 
    print ("xmin: ", xMin, "   xmax: ",xMax, "   middle: ",(((xMax-xMin)/2)+xMin))
    #Set area to rotate camera if person is outside area
    person_middle = ((xMax-xMin)/2)+xMin
    left_wall = .49
    right_wall = .51
    print("Person l r and m: ",left_wall,person_middle,right_wall)

    if person_middle < left_wall:
        if currentCamAngle < 5:
            currentCamAngle= 5
        # if person_middle < int(frame.shape[1] *.5):
        currentCamAngle -= 1
        tracker.rotateYaw(currentCamAngle)            
    if person_middle > right_wall:
        if currentCamAngle > 175:
            currentCamAngle = 175
    # if person_middle > int(frame.shape[1] *.5):
        currentCamAngle += 1
        tracker.rotateYaw(currentCamAngle)
    print("from demo current cam angle:", currentCamAngle)
    # return frame
#to record video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while True:
    # Run blazepose on next frame
    landmarks = np.array([])
    frame0, body, landmarks = pose.next_frame()

    just_cam = frame0
    just_cam = renderer.draw(just_cam,body)
    #to record cam frame to video file
    hsv = cv2.cvtColor(just_cam, cv2.COLOR_BGR2HSV)
    hsv = cv2.resize(hsv,(640,480),interpolation = cv2.INTER_AREA)

    cv2.imshow("HSV",hsv)
    out.write(hsv)
    NoneType = type(None)
    if type(landmarks) != NoneType:
        print("Landmarks: ",landmarks)
        print("just cam shape[1]: ",just_cam.shape[1])
        # rotate_cam(landmarks)# send landmarks and image to tracker to move camera, return image 

    #create blank canvas(can adjust colors) same size as user's screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # print("Screen size: ", screen_width,screen_height)
    bg_canvas = np.zeros((screen_height,screen_width,3), np.uint8)
    # print("bg_canvas shape",bg_canvas.shape)

    # #paste example image on bg_canvas
    # img = cv2.imread(current_pose_list[current_pose])   
    # ratio = img.shape[0]/img.shape[1] #adjust example size
    # example_width = 200
    # example_height = int((200 * ratio))
    # img2 = cv2.resize(img,(example_width,example_height),interpolation = cv2.INTER_AREA)
    # bg_canvas[0:img2.shape[0],int(screen_width/2):int(screen_width/2)+img2.shape[1]] = img2

    #resize cam image
    cam_ratio = just_cam.shape[0]/just_cam.shape[1]
    cam_width = bg_canvas.shape[1]/2
    cam_height = cam_width*cam_ratio
    # print("cam ration:",cam_ratio)
    cam_dim = (int(cam_width),int(cam_height))
    just_cam = cv2.resize(just_cam,cam_dim,interpolation = cv2.INTER_AREA)
    just_cam_flipped = cv2.flip(just_cam,1)
    just_cam_joined = cv2.hconcat([just_cam,just_cam_flipped])
    blank_bottom = np.zeros((just_cam_joined.shape[0],just_cam_joined.shape[1],3), np.uint8)
    full_layout = cv2.vconcat([just_cam_joined,blank_bottom])
    cv2.imshow("blank canvas", full_layout)

    bg_canvas[0:just_cam_joined.shape[0],0:just_cam_joined.shape[1]] = just_cam_joined #paste cam output on bg_canvas

    if frame0 is None: break
    
    # print("current pose number : ", desired_pose)
    NoneType = type(None)
    bg_canvas = np.zeros((int(cam_height),int(cam_height),3), np.uint8)
    if type(landmarks) != NoneType:
        #draw landmarks on area below cam image
        canvas_max_width = cam_width
        canvas_max_height = canvas_max_width * cam_ratio
        positions = []
        for landmark in landmarks:
            x,y,z = landmark
            x_loc = int(x*canvas_max_width)
            y_loc = int(y*canvas_max_height+cam_height)
            positions.append([x_loc,y_loc])
            cv2.circle(full_layout,(x_loc,y_loc), 5, (200,100,255), -1)

        # for line in LINES_BODY:
        #     bg_canvas = cv2.line(bg_canvas,positions[line[0]],positions[line[1]],(0, 255, 0),8)

    cv2.imshow("Yoga demo",full_layout)


############################# end new stuff ########################




    # key = renderer.waitKey(delay=1)
    # Wait for 'q' key to stop the program 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
out.release()#close video recording

# renderer.exit()
# pose.exit()
cv2.destroyAllWindows()