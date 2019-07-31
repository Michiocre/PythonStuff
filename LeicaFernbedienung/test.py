import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN) #UP
GPIO.setup(38, GPIO.IN) #RIGHT
GPIO.setup(37, GPIO.IN) #DOWN
GPIO.setup(36, GPIO.IN) #LEFT
GPIO.setup(35, GPIO.IN) #MAIN

keyUp = 0
keyDown = 0
keyRight = 0
keyLeft = 0
keyMain = 0

keyUpO = 0
keyDownO = 0
keyRightO = 0
keyLeftO = 0
keyMainO = 0

while 1:
    if (GPIO.input(40)):
        print('UP')
    if (GPIO.input(38)):
        print('RIGHT')
    if (GPIO.input(37)):
        print('DOWN')
    if (GPIO.input(36)):
        print('LEFT')
    if (GPIO.input(35)):
        print('MAIN')
