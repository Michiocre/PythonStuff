import time
import os
import threading
import pynput
# from pynput.mouse import Button, Controller
# from pynput.keyboard import Listener, KeyCode, Key, Controller
from pycaw.pycaw import AudioUtilities

z_start_stop_key = pynput.keyboard.Key.f6
f_start_stop_key = pynput.keyboard.Key.f7
exit_key = pynput.keyboard.Key.f12

sessions = AudioUtilities.GetAllSessions()
clear = lambda: os.system('cls')
print("Press F6 to start the Zombie killing script, F7 for the fishing script. Press F12 to close this programm.")

def emptyFunction():
    return

class ClickerThread(threading.Thread):
    def __init__(self, name, delay, button, button2 = None, extraFunction = emptyFunction):
        super(ClickerThread, self).__init__()
        self.delay = delay
        self.button = button
        self.button2 = button2
        self.running = False
        self.program_running = True
        self.name = name
        self.counter = 0
        self.extraFunction = extraFunction

    def start_clicking(self):
        print(self.name, " is running right now.")
        self.running = True
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.name() == "javaw.exe":
                volume.SetMute(1, None)

    def stop_clicking(self):
        self.counter = 0
        clear()
        print("Press F6 to start the Zombie killing script, F7 for the fishing script. Press F12 to close this programm.")
        if self.button2 is not None:
            mouse.release(self.button2)
        self.running = False
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.name() == "javaw.exe":
                volume.SetMute(0, None)

    def exit(self):
        print("Cya")
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                self.counter += 1
                if self.counter == 1:
                    self.counter = 0
                    self.extraFunction()
                mouse.click(self.button)
                if self.button2 is not None:
                    mouse.press(self.button2)
                time.sleep(self.delay)
            time.sleep(0.1)

def swapOffHand():
    keyboard.press('f')
    time.sleep(0.1)
    keyboard.release('f')
    time.sleep(0.5)
    keyboard.press('f')
    time.sleep(0.1)
    keyboard.release('f')


mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()
zClick_thread = ClickerThread("ZombieScript", 5, pynput.mouse.Button.left, pynput.mouse.Button.right, swapOffHand)
zClick_thread.start()

fClick_thread = ClickerThread("FishingScript", 1, pynput.mouse.Button.right)
fClick_thread.start()

def on_press(key):
    if key == z_start_stop_key:
        if zClick_thread.running:
            zClick_thread.stop_clicking()
        else:
            if fClick_thread.running:
                fClick_thread.stop_clicking()
            zClick_thread.start_clicking()
    if key == f_start_stop_key:
        if fClick_thread.running:
            fClick_thread.stop_clicking()
        else:
            if zClick_thread.running:
                zClick_thread.stop_clicking()
            fClick_thread.start_clicking()
    elif key == exit_key:
        fClick_thread.exit()
        zClick_thread.exit()
        listener.stop()

with pynput.keyboard.Listener(on_press=on_press) as listener:
    listener.join()