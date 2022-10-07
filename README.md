# tiffainy_track_cam
Tracking camera system for the OAK camera

Full instructions in the documentation.pdf

All 3D printable parts available on Thingiverse: https://www.thingiverse.com/thing:4924306

Follow the documentation.pdf document for instructions on assembly and setting up Tiff(AI)ny
Youtube assemby instructions:

As with other depthai projects, just install the requirements:
pip install -r requirements.txt

How to install the pyFirmata firmware on the Arduino:
Youtube instructions: https://youtu.be/Dbi4yGyDmEQ

To test the servos to ensure they function properly:
Youtube instructions: https://youtu.be/hb-JovBAJS8
Run the servo_test_and_home.py file

Run the tracker_servo.py file to tune the servos and set the home position.
Youtube instructions: https://youtu.be/UHs9vj-bUZ0

Currently, we have a demo running the BlazePose human pose estimation network.
Just run the BlazePose_demo.py file

The code to track and control the devide are located in the 
BlazeposeRenderer.py
file.

More demos coming soon!
