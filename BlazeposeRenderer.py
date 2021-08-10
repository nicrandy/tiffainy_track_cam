import cv2
import numpy as np
import tracker_servo as  tracker
# import open3d as o3d
# from o3d_utils import create_segment, create_grid

# LINES_BODY is used when drawing the skeleton onto the source image. 
# Each variable is a list of continuous lines.
# Each line is a list of keypoints as defined at https://google.github.io/mediapipe/solutions/pose.html#pose-landmark-model-blazepose-ghum-3d
LINES_BODY = [[28,30,32,28,26,24,12,11,23,25,27,29,31,27], 
                [23,24],
                [22,16,18,20,16,14,12], 
                [21,15,17,19,15,13,11],
                [8,6,5,4,0,1,2,3,7],
                [10,9],
                ]

# LINE_MESH_BODY and COLORS_BODY are used when drawing the skeleton in 3D. 
rgb = {"right":(0,1,0), "left":(1,0,0), "middle":(1,1,0)}
LINE_MESH_BODY = [[9,10],[4,6],[1,3],
                    [12,14],[14,16],[16,20],[20,18],[18,16],
                    [12,11],[11,23],[23,24],[24,12],
                    [11,13],[13,15],[15,19],[19,17],[17,15],
                    [24,26],[26,28],[32,30],
                    [23,25],[25,27],[29,31]]

COLORS_BODY = ["middle","right","left",
                    "right","right","right","right","right",
                    "middle","middle","middle","middle",
                    "left","left","left","left","left",
                    "right","right","right","left","left","left"]
COLORS_BODY = [rgb[x] for x in COLORS_BODY]

class BlazeposeRenderer:
    def __init__(self,
                pose,
                show_3d=False,
                output=None):
        self.pose = pose
        self.show_3d = show_3d

        # Rendering flags
        self.show_rot_rect = False
        self.show_landmarks = True
        self.show_score = False
        self.show_fps = True

        if self.show_3d:

            self.vis3d = o3d.visualization.Visualizer()
            self.vis3d.create_window() 
            opt = self.vis3d.get_render_option()
            opt.background_color = np.asarray([0, 0, 0])
            z = min(pose.img_h, pose.img_w)/3
            self.grid_floor = create_grid([0,pose.img_h,-z],[pose.img_w,pose.img_h,-z],[pose.img_w,pose.img_h,z],[0,pose.img_h,z],5,2, color=(1,1,1))
            self.grid_wall = create_grid([0,0,z],[pose.img_w,0,z],[pose.img_w,pose.img_h,z],[0,pose.img_h,z],5,2, color=(1,1,1))
            self.vis3d.add_geometry(self.grid_floor)
            self.vis3d.add_geometry(self.grid_wall)
            view_control = self.vis3d.get_view_control()
            view_control.set_up(np.array([0,-1,0]))
            view_control.set_front(np.array([0,0,-1]))

        if output is None:
            self.output = None
        else:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            self.output = cv2.VideoWriter(output,fourcc,pose.video_fps,(pose.img_w, pose.img_h)) 

    def draw_landmarks(self, body):
        if self.show_rot_rect:
            cv2.polylines(self.frame, [np.array(body.rect_points)], True, (0,255,255), 2, cv2.LINE_AA)
        if self.show_landmarks:                
            list_connections = LINES_BODY
            lines = [np.array([body.landmarks[point,:2] for point in line]) for line in list_connections]
            # lines = [np.array([body.landmarks_padded[point,:2] for point in line]) for line in list_connections]
            cv2.polylines(self.frame, lines, False, (255, 180, 90), 2, cv2.LINE_AA)
            
############our code for tracker cam#####################
            #get the far left and far right X position output of the landmarks
            xMin = 1000000
            xMax = -100000
            yMin = 1000000
            yMax = -100000
            for i,x_y in enumerate(body.landmarks[:self.pose.nb_kps,:2]):
                x = x_y[0]
                y = x_y[1]
                if x > xMax:
                    xMax = x 
                if x < xMin:
                    xMin = x 
                if y > yMax:
                    yMax = y
                if y < yMin:
                    yMin = y
# this colors the circles for the rendered lines (not part of tracking cam)
                if i > 10:
                    color = (0,255,0) if i%2==0 else (0,0,255)
                elif i == 0:
                    color = (0,255,255)
                elif i in [4,5,6,8,10]:
                    color = (0,255,0)
                else:
                    color = (0,0,255)
                cv2.circle(self.frame, (x_y[0], x_y[1]), 4, color, -11)

############our code for tracker cam#####################
            xMiddle = ((xMax-xMin)/2)+xMin
            yMiddle = ((yMax-yMin)/2)+yMin
            frameXmiddle = int(self.frame.shape[1]/2)
            frameYmiddle = int(self.frame.shape[0]/2)
            #draw a circle in the middle of the frame
            cv2.circle(self.frame, (int(frameXmiddle),int(frameYmiddle)), 35, (220,80,149), -1)
            #draw a circle in the middle of our target we want to track
            cv2.circle(self.frame, (int(xMiddle),int(yMiddle)), 20, (100,150,200), -1)

            #set the threshold on the movement bounding box
            #adjust the values (based on with of input frame)
            left_wall = .45 * self.frame.shape[1]
            right_wall = .55 *self.frame.shape[1]
            ceiling = .65 * self.frame.shape[0]
            ground = .55 * self.frame.shape[0] 

            if xMiddle < left_wall:
                tracker.left()
            if xMiddle > right_wall:
                tracker.right()
            if yMiddle > ceiling:
                tracker.down()
            if yMiddle < ground:
                tracker.up()


    def draw(self, frame, body):
        self.frame = frame
        if body:
            self.draw_landmarks(body)
            self.body = body
        elif self.frame is None:
            self.frame = frame
            self.body = None
        return self.frame
    
    def exit(self):
        if self.output:
            self.output.release()

    def waitKey(self, delay=1):
        key = cv2.waitKey(delay) 
        return key
