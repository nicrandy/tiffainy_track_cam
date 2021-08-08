#Use the 'a' key to rotate left, 's' to rotate right, 'q' to exit program
#adjust speed variable to go faster or slower



from pyfirmata import Arduino, util, SERVO
import time
import keyboard

######## change testing to true during testing, false for implementation
testing = True

board = Arduino('COM4')
time.sleep(1)
print("On")
#set the correct pins for servos
pinYaw = 5
pinPitch = 9
speed = .015 # increase to go slower, decrease to go faster

#set the home angle for servos
yawHomeAngle = 64
pitchHomeAngle = 120
pitchAngle = pitchHomeAngle
yawAngle = yawHomeAngle

#set the min and max rotation area
yawMax = 130
yawMin = 0
pitchMax = 145
pitchMin = 80

board.digital[pinYaw].mode = SERVO
board.digital[pinYaw].write(yawHomeAngle)
time.sleep(.5)
board.digital[pinPitch].mode = SERVO
board.digital[pinPitch].write(pitchHomeAngle)
print("Tracker cam running")
time.sleep(2)


def up(angle):
	if angle > pitchMax:
		angle = pitchMax
	print("Move Pitch to angle: ",angle)
	board.digital[pinPitch].write(angle)
	time.sleep(speed)

def down(angle):
	if angle < pitchMin:
		angle = pitchMin
	print("Move Pitch to angle: ",angle)
	board.digital[pinPitch].write(angle)
	time.sleep(speed)

def left(angle):
	if angle > yawMax:
		angle = yawMax
	print("Move Yaw to angle: ", angle)
	board.digital[pinYaw].write(angle)
	time.sleep(speed)

def right(angle):
	if angle < yawMin:
		angle = yawMin
	print("Move Yaw to angle: ", angle)
	board.digital[pinYaw].write(angle)
	time.sleep(speed)



while testing:
	if keyboard.is_pressed("q"):
		board.exit()
		break
	if keyboard.is_pressed("a"):
		pitchAngle+=1
		left(pitchAngle)
	if keyboard.is_pressed("d"):
		pitchAngle-=1
		right(pitchAngle)
	if keyboard.is_pressed("w"):
		yawAngle+=1
		up(yawAngle)
	if keyboard.is_pressed("s"):
		yawAngle-=1
		down(yawAngle)



