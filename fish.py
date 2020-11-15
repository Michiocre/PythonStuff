from PIL import ImageGrab
import win32api
import pyautogui
from queue import Queue
import time

key1 = 0
key0 = 0
key1Old = 0
key0Old = 0

def checkFish():
    img = ImageGrab.grab(bbox=(750,225,800,275))
    px = img.load()
    for y in range(0, 50, 1):
        for x in range(0, 50, 1):
            color = px[x, y]
            if (color[0] > 230 and color[1] > 230 and color[2] > 120):
                    return True
    return False

def key1Update():
    global key1, key1Old
    key1 = win32api.GetKeyState(ord('1'))
    val = False
    if(key1Old >= 0 and key1 < 0):
        val = True
    key1Old = key1
    return val

def key0Update():
    global key0, key0Old
    key0 = win32api.GetKeyState(ord('0'))
    val = False
    if(key0Old >= 0 and key0 < 0):
        val = True
    key0Old = key0
    return val

def fishMain():
    print("Fishmode engaged")
    mem = []
    state = False
    oldState = False
    while not key0Update():
        mem.insert(0, checkFish())
        if(len(mem) > 9):
            mem.pop()
        if any(mem):
            state = True
        else:
            state = False
        if (oldState and not state):
            pyautogui.press('2')
            time.sleep(15)
            pyautogui.press('1')
        oldState = state
    print("Fishmode disabled")

while not key0Update():
    if key1Update():
        print('yes')
        pyautogui.press('end')
        fishMain()