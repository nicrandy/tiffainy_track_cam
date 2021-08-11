####################
# This code is used to test the servos and also to control the servos
# Use the 'a' key to rotate left, 's' to rotate right...., 'q' to exit program

from pyfirmata import Arduino, util, SERVO
import time
import keyboard

######## change testing to true during testing, false for implementation
testing = False

#Set the board below to the correct port (located in device manager)
board = Arduino('COM4')
time.sleep(1)

#set the correct pins for servos
pinYaw = 5
pinPitch = 9
speed = .025 # increase to go slower, decrease to go faster

#set the home angle for servos
yawHomeAngle = 90
pitchHomeAngle = 90
pitchAngle = pitchHomeAngle
yawAngle = yawHomeAngle

#adjust the angle for each movement (how many degrees to move each time)
# must be a whole number (1 is slow, 3 is fast)
pitchMovement = 1
yawMovement = 2

#set the min and max rotation area
yawMax = 170
yawMin = 10
pitchMax = 140
pitchMin = 60

#this part sets the servos to the home position
board.digital[pinYaw].mode = SERVO
board.digital[pinYaw].write(yawHomeAngle)
time.sleep(.5)
board.digital[pinPitch].mode = SERVO
board.digital[pinPitch].write(pitchHomeAngle)
print("Tracker running")
time.sleep(2)


def up():
	global pitchAngle
	pitchAngle += pitchMovement
	if pitchAngle > pitchMax:
		pitchAngle = pitchMax
	print("Move Pitch up to angle: ",pitchAngle)
	board.digital[pinPitch].write(pitchAngle)
	time.sleep(speed)

def down():
	global pitchAngle
	pitchAngle -= pitchMovement
	if pitchAngle < pitchMin:
		pitchAngle = pitchMin
	print("Move Pitch down to angle: ",pitchAngle)
	board.digital[pinPitch].write(pitchAngle)
	time.sleep(speed)

def left():
	global yawAngle
	yawAngle += yawMovement
	if yawAngle > yawMax:
		yawAngle = yawMax
	print("Move Yaw left to angle: ", yawAngle)
	board.digital[pinYaw].write(yawAngle)
	time.sleep(speed)

def right():
	global yawAngle
	yawAngle -= yawMovement
	if yawAngle < yawMin:
		yawAngle = yawMin
	print("Move Yaw right to angle: ", yawAngle)
	board.digital[pinYaw].write(yawAngle)
	time.sleep(speed)



while testing:
	if keyboard.is_pressed("q"):
		board.exit()
		break
	if keyboard.is_pressed("a"):
		left()
	if keyboard.is_pressed("d"):
		right()
	if keyboard.is_pressed("w"):
		up()
	if keyboard.is_pressed("s"):
		down()



