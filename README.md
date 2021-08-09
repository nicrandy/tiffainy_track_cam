# tiffainy_track_cam
Tracking camera system for the OAK camera

All 3D printable parts available on Thingiverse: https://www.thingiverse.com/thing:4924306

Follow the documentation.pdf document for instructions on assembly and setting up Tiff(AI)ny

As with other depthai projects, just install the requirements:
pip install -r requirements.txt

Run the tracker_servo.py file to tune the servos and set the home position.
Instructions on how to do this available on Youtube at:

Currently, we have a demo running the BlazePose human pose estimation network.
Just run the BlazePose_demo.py file

The code to track and control the devide are located in the 
BlazeposeRenderer.py
file.

More demos coming soon!
