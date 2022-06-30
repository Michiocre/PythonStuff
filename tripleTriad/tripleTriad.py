import numbers
import sys
import os
import time
import math
import argparse
import json
import numpy as np
import pyautogui
import win32api
import cv2
import pytesseract
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab, Image, ImageStat
from distutils.dir_util import copy_tree 
import matplotlib.pyplot as plt

key1 = 0
key0 = 0
key1Old = 0
key0Old = 0

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

def playCard(deckI, boardI):
    if not board[boardI] is None:
        return False
    if myDeck[deckI] is None:
        return False
        
    board[boardI] = [True, myDeck[deckI]]
    myDeck[deckI] = None
            
    x = boardI % 3
    y = math.floor(boardI / 3)

    if x - 1 >= 0 and board[boardI - 1] is not None:
        if board[boardI][1][0] > board[boardI - 1][1][2]:
            board[boardI - 1][0] = True
    if x + 1 <= 2 and board[boardI + 1] is not None:
        if board[boardI][1][2] > board[boardI + 1][1][0]:
            board[boardI + 1][0] = True
    if y - 1 >= 0 and board[boardI - 3] is not None:
        if board[boardI][1][1] > board[boardI - 3][1][3]:
            board[boardI - 3][0] = True
    if y + 1 <= 2 and board[boardI + 3] is not None:
        if board[boardI][1][3] > board[boardI + 3][1][1]:
            board[boardI + 3][0] = True
    return True

def enemyCard(deckI, boardI):
    if not board[boardI] is None:
        return False
    if enemyDeck[deckI] is None:
        return False
        
    board[boardI] = [False, enemyDeck[deckI]]
    enemyDeck[deckI] = None

    x = boardI % 3
    y = math.floor(boardI / 3)

    if x - 1 >= 0 and board[boardI - 1] is not None:
        if board[boardI][1][0] > board[boardI - 1][1][2]:
            board[boardI - 1][0] = False
    if x + 1 <= 2 and board[boardI + 1] is not None:
        if board[boardI][1][2] > board[boardI + 1][1][0]:
            board[boardI + 1][0] = False
    if y - 1 >= 0 and board[boardI - 3] is not None:
        if board[boardI][1][1] > board[boardI - 3][1][3]:
            board[boardI - 3][0] = False
    if y + 1 <= 2 and board[boardI + 3] is not None:
        if board[boardI][1][3] > board[boardI + 3][1][1]:
            board[boardI + 3][0] = False
    return True

def getScore():
    score = 0
    for i in range(len(board)):
        if board[i] is not None:
            if (board[i][0]):
                score += 1
    return score

def boardFull():
    for i in range(len(board)):
        if board[i] is None:
            return False
    return True

def minmax(depth):
    global board, myDeck
    oldBoard = board.copy()
    oldDeck = myDeck.copy()
    best = [None, None, -1]
    for deckI in range(len(myDeck)):
        if myDeck[deckI] is None:
            continue
        if chaos and myDeck[deckI][4] < 60 and depth == 0:
                continue

        for boardI in range(len(board)):
            if not playCard(deckI, boardI):
                continue
            
            if boardFull() or depth == 4:
                score = getScore()
            else: 
                score = minmaxEnemy(depth + 1)[2]

            #print('    ' * depth, deckI, boardI, score)    
            
            if score > best[2]:
                best[0] = deckI
                best[1] = boardI
                best[2] = score
            board = oldBoard.copy()
            myDeck = oldDeck.copy()
    return best

def minmaxEnemy(depth):
    global board, enemyDeck
    oldBoard = board.copy()
    oldEDeck = enemyDeck.copy()
    best = [None, None, 10000000]
    for deckI in range(len(enemyDeck)):
        for boardI in range(len(board)):
            if not enemyCard(deckI, boardI):
                continue

            if boardFull() or depth == 3:
                score = getScore()
            else: 
                score = minmax(depth + 1)[2]

            #print('    ' * depth, deckI, boardI, score)   

            if score < best[2]:
                best[0] = deckI
                best[1] = boardI
                best[2] = score
            
            board = oldBoard.copy()
            enemyDeck = oldEDeck.copy()
    return best

def convertToCv2(img):
    img = img.convert('RGB') 

    img = np.array(img) 
    # Convert RGB to BGR
    return img

def saveImg(path, fileName, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    Path(path).mkdir(parents=True, exist_ok=True)
    cv2.imwrite(os.path.join(path, fileName), img)

def loadImg(path, grayscale = False):
    if grayscale:
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def getCardData(image, basePath):
    if args.debug:
        saveImg(basePath, 'fullImage.png', cardImg)

    values = cardNumbers(cardImg, basePath)

    card = {
        'position': {
            'x': x,
            'y': y
        },
        'values': values
    }

    return card

def cardNumbers(image, basePath):
    numberSize = (13, 11)
    numberPos = {
        'left': (27, 94),
        'up': (39, 88),
        'right': (51, 94),
        'down': (39, 100)
    }

    values = {
        'left': None,
        'up': None,
        'right': None,
        'down': None
    }
    
    for numberKey in numberPos:
        best = {
            'number': None,
            'diff': None
        }
        x = numberPos[numberKey][0]
        y = numberPos[numberKey][1]
        numberImg = image[y:y + numberSize[1], x:x + numberSize[0]]
        if args.debug:
            saveImg(basePath, '_' + numberKey + '_raw.png', numberImg)

        grayImg = cv2.cvtColor(numberImg, cv2.COLOR_BGR2GRAY)

        if args.debug:
            saveImg(basePath, '_' + numberKey + '_gray.png', grayImg)

        brightestPixel = np.amax(grayImg)
        ret, threshold = cv2.threshold(grayImg, brightestPixel - 22, 255, cv2.THRESH_BINARY)

        if args.debug:
            saveImg(basePath, '_' + numberKey + '_threshold.png', threshold)
        for i in range(len(chars)):
            errorL2 = cv2.norm(threshold, chars[i], cv2.NORM_L2)
            similarity = 1 - errorL2 / (numberSize[0] * numberSize[1])
            
            if best['diff'] is None:
                best['number'] = i + 1
                best['diff'] = similarity
                continue
            
            if best['diff'] < similarity:
                best['number'] = i + 1
                best['diff'] = similarity

        if best['number'] <= 10:
            values[numberKey] = best['number']

    if values['left'] is None and values['up'] is None and values['right'] is None and values['down'] is None:
        return None
    if args.debug:
        if (values['left'] is None or values['up'] is None or values['right'] is None or values['down'] is None):
            print('ERROR: One ore more numbers were not detected correctly', values)
            outPath = 'outputs/errors/numbers/' + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            copy_tree(basePath, outPath)
            with open(outPath + '/values.json', 'w') as f:
                    f.write(json.dumps(values))


    return values

#Handle arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--debug', action="store_true", help='will write images into the output folder and add extra logs')
parser.add_argument('--local', action="store_true", help='start the program with a image from the output folder')

args = parser.parse_args()

#Load in static images
chars = []
for filename in os.listdir('chars'):
    chars.append(loadImg('chars/' + filename, True))
cornerTemplate = loadImg('inputs/cornerTemplate.png')
hiddenCardTemplate = loadImg('inputs/hiddenCardTemplate.png', True)
yourTurnTemplate = loadImg('inputs/yourTurnTemplate.png', True)

roundCounter = 0

#Wait for start loop
if not args.local:
    while not key1Update():
        continue

#Main Loop (cancel with ctrl+c)
while True:
    if args.local: 
        fullScreen = loadImg('inputs/local2.png')
    else:
        fullScreen = convertToCv2(ImageGrab.grab())

    if (args.debug):
        saveImg('outputs', '01_fullScreen.png', fullScreen)

    #Template Matching

    w, h = cornerTemplate.shape[:2]

    res = cv2.matchTemplate(fullScreen, cornerTemplate, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    fullScreenCopy = fullScreen.copy()
    cv2.rectangle(fullScreenCopy, top_left, bottom_right, 255, 2)

    #Crop image
    playWindow = fullScreen[top_left[1]:top_left[1] + 460, top_left[0]:top_left[0] + 1106]
    if args.debug:
        saveImg('outputs', '02_playWindow.png', playWindow)

    #Find the your turn indicator
    yourTurn = cv2.cvtColor(playWindow[35:55, 35:55], cv2.COLOR_BGR2GRAY)
    if args.debug:
        saveImg('outputs', '03_yourTurn.png', yourTurn)

    errorL2 = cv2.norm(yourTurn, yourTurnTemplate, cv2.NORM_L2)
    similarity = 1 - errorL2 / (20 * 20)

    if similarity < 0:
        time.sleep(1)
        continue
    #This code will get executed when the your turn indicator is present

    if args.debug:
        saveImg('outputs/' + str(roundCounter), '01_playWindow.png', playWindow)

    #Extract Rules
    ruleView = playWindow[8:88, 816:1076]
    if args.debug:
        saveImg('outputs/' + str(roundCounter), '02_rules.png', ruleView)

    rulesString = pytesseract.image_to_string(ruleView)
    rules = {
        'chaos': 'Chaos' in rulesString
    }

    print('NOTICE: Enabled Rules: ', rules)

    #Setting up data structures
    board = np.empty(3, dtype=object)
    for y in range(len(board)):
        board[y] = np.empty(3, dtype=object)

    decks = {
        'player': np.empty(5, dtype=object),
        'enemy': np.empty(5, dtype=object)
    }
        
    print(board)
    print(decks)

    cardSize = (91, 119)
    deckCardOffset = (108, 138)
    boardOffset = (136, 136)
    gridStart = {
        'player': (15, 173),
        'enemy': (785, 173),
        'board': (373, 35)
    }


    #Read in the decks
    for key in decks:
        for i in range(len(decks[key])):
            basePath = 'outputs/' + str(roundCounter) + '/' + key + '/' + str(i)

            j = math.floor(i / 3)
            x = gridStart[key][0] + (i % 3) * deckCardOffset[0] + (j * 54)
            y = gridStart[key][1] + j * deckCardOffset[1]

            cardImg = playWindow[y:y + cardSize[1], x:x + cardSize[0]]
            decks[key][i] = getCardData(cardImg, basePath)

            if key == 'player':
                #Brightness Check
                cornerImg = cv2.cvtColor(cardImg[0:3, 0:3], cv2.COLOR_BGR2GRAY)
                decks[key][i]['active'] = cv2.mean(cornerImg)[0] > 100
            else:
                #Check if card is hidden or already used
                cornerImg = cv2.cvtColor(cardImg[0:16, 0:16], cv2.COLOR_BGR2GRAY)
                errorL2 = cv2.norm(cornerImg, hiddenCardTemplate, cv2.NORM_L2)
                similarity = abs(1 - errorL2 / (16 * 16))

                decks[key][i]['hidden'] = similarity < 0.1


            if args.debug:
                with open(basePath + '/values.json', 'w') as f:
                    f.write(json.dumps(decks[key][i]))

    #Read in the board
    for i in range(len(board)):
        for j in range(len(board[i])):
            basePath = 'outputs/' + str(roundCounter) + '/board/' + str(i) + '-' + str(j)

            x = gridStart['board'][0] + j * boardOffset[0]
            y = gridStart['board'][1] + i * boardOffset[1]

            cardImg = playWindow[y:y + cardSize[1], x:x + cardSize[0]]
            board[i][j] = getCardData(cardImg, basePath)

            if board[i][j]['values'] is not None:

                #Color Check
                redCounter = 0
                blueCounter = 0

                colors = {
                    'red': (103, 40, 41),
                    'blue': (41, 71, 103),
                    'tolerance': 10
                }

                colorImg = cardImg.copy()

                for pix in range(cardImg.shape[0]):
                    for piy in range(cardImg.shape[1]):
                        pixel = cardImg[pix, piy]
                        channelCounterR = 0
                        channelCounterB = 0
                        for pii in range(len(pixel)):
                            if pixel[pii] > colors['red'][pii] - colors['tolerance'] and pixel[pii] < colors['red'][pii] + colors['tolerance']:
                                channelCounterR += 1
                            elif pixel[pii] > colors['blue'][pii] - colors['tolerance'] and pixel[pii] < colors['blue'][pii] + colors['tolerance']:
                                channelCounterB += 1
                            else:
                                break
                        if channelCounterR == 3:
                            redCounter += 1
                            colorImg[pix, piy] = colors['red']
                        elif channelCounterB == 3:
                            blueCounter += 1
                            colorImg[pix, piy] = colors['blue']
                        else:
                            colorImg[pix, piy] = 0

                if args.debug:
                    saveImg(basePath, 'colors.png', colorImg)

                board[i][j]['owner'] = 'player' if redCounter < blueCounter else 'enemy'

                if args.debug:
                    if (abs(redCounter - blueCounter) < 20):
                        print('WARNING: Some color differences are very small, maybe adjust the threshold')
                        copy_tree(basePath, 'outputs/errors/colors/' + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))

            if args.debug:
                with open(basePath + '/values.json', 'w') as f:
                    f.write(json.dumps(board[i][j]))

    def defaultSerializer(obj):
        return 'Image'
        
    status = {
        'rules': rules,
        'decks': decks,
        'board': board
    }



    #Cleanup for next round
    if args.debug:
        with open('outputs/' + str(roundCounter) + '/03_values.json', 'w') as f:
            f.write(json.dumps(status, default=lambda o: o.tolist()))
    roundCounter +=1
    if args.local:
        break


