#Use the 'a' key to rotate left, 's' to rotate right, 'q' to exit program
#adjust speed variable to go faster or slower

from pyfirmata import Arduino, util, SERVO
import time
import keyboard

board = Arduino('COM4')
time.sleep(1)
print("Board On")
pin = 3

speed = .015 # increase to go slower, decrease to go faster
start_angle = 90

board.digital[pin].mode = SERVO
board.digital[pin].write(start_angle)

print("Servo home")
time.sleep(1)


def rotate(angle):
	print("Move servo to angle: ",angle)
	board.digital[pin].write(angle)
	time.sleep(speed)


while True:
	if keyboard.is_pressed("q"):
		board.exit()
		break
	if keyboard.is_pressed("l"):
		start_angle+=1
		rotate(start_angle)
		if start_angle > 180:
			start_angle = 180
	if keyboard.is_pressed("r"):
		start_angle-=1
		rotate(start_angle)
		if start_angle <= 1:
			start_angle = 1
	if keyboard.is_pressed("h"):
		start_angle = 90
		rotate(start_angle)
		time.sleep(1)




