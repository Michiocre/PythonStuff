import sys
import os
import time
import math
import argparse
import json
import copy
import numpy as np
import pyautogui
import win32api
import cv2
import pytesseract
import random
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

def boardFull(board):
        for y in range(len(board)):
            for x in range(len(board[y])):
                if board[y][x]['values'] is None:
                    return False
        return True

def getScore(board):
    score = 0
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x]['values'] is not None:
                if board[y][x]['owner'] == 'player':
                    score += 1
                else:
                    score -= 1
    return score

def playCard(board, decks, player, x, y, i, rules):
    board[y][x]['values'] = decks[player][i]['values']
    board[y][x]['owner'] = player

    decks[player][i]['values'] = None

    swaps = []

    if y > 0:
        if board[y - 1][x]['values'] is not None:
            if board[y][x]['values']['up'] > board[y - 1][x]['values']['down']:
                board[y - 1][x]['owner'] = player
                swaps.append([y-1, x])
    if y < 2:
        if board[y + 1][x]['values'] is not None:
            if board[y][x]['values']['down'] > board[y + 1][x]['values']['up']:
                board[y + 1][x]['owner'] = player
                swaps.append([y-1, x])
    if x > 0:
        if board[y][x - 1]['values'] is not None:
            if board[y][x]['values']['left'] > board[y][x - 1]['values']['right']:
                board[y][x - 1]['owner'] = player
                swaps.append([y, x - 1])
    if x < 2:
        if board[y][x + 1]['values'] is not None:
            if board[y][x]['values']['right'] > board[y][x + 1]['values']['left']:
                board[y][x + 1]['owner'] = player
                swaps.append([y, x + 1])

    return swaps

def undoPlay(board, decks, player, x, y, i, swaps):
    decks[player][i]['values'] = board[y][x]['values']
    board[y][x]['owner'] = None
    board[y][x]['values'] = None

    for swapI in range(len(swaps)):
        board[swaps[swapI][0]][swaps[swapI][1]]['owner'] = 'enemy' if player == 'player' else 'player'

def getExposedSides(board, x, y):
    sidesOpen = 0
    sum = 0
    if y > 0:
        if board[y - 1][x]['values'] is None:
            sidesOpen += 1
            sum += board[y][x]['values']['up']
    if y < 2:
        if board[y + 1][x]['values'] is None:
            sidesOpen += 1
            sum += board[y][x]['values']['down']
    if x > 0:
        if board[y][x - 1]['values'] is None:
            sidesOpen += 1
            sum += board[y][x]['values']['left']
    if x < 2:
        if board[y][x + 1]['values'] is None:
            sidesOpen += 1
            sum += board[y][x]['values']['right']
    if sidesOpen == 0:
        return 10000
    return sum / sidesOpen

def minmax(board, decks, player, depth, maxDepth, rules):
    scores = []

    for i in range(len(decks[player])):
        if decks[player][i]['values'] is None:
            continue
        if depth == 0 and rules['chaos'] == True and not decks[player][i]['active']:
            continue
        for y in range(len(board)):
            for x in range(len(board[y])):
                if board[y][x]['values'] is not None:
                    continue

                swaps = playCard(board, decks, player, x, y, i, rules)

                score = getScore(board)
                exposedValues = getExposedSides(board, x, y)
                
                # print([[i, x, y], score])
                # print(board)

                if boardFull(board) or depth >= maxDepth:
                    scores.append([[i, x, y], score, exposedValues])
                else:
                    futureMove = minmax(board, decks, 'enemy' if player == 'player' else 'player', depth + 1, maxDepth, rules)
                    scores.append([[i, x, y], futureMove[1], exposedValues])

                undoPlay(board, decks, player, x, y, i, swaps)

    best = None

    for i in range(len(scores)):
        if best is None:
            best = i
            continue
        if player == 'player':
            if scores[best][1] < scores[i][1]:
                best = i
            elif scores[best][1] == scores[i][1]:
                if scores[best][2] < scores[i][2]:
                    best = i
        else: 
            if scores[best][1] > scores[i][1]:
                best = i
            elif scores[best][1] == scores[i][1]:
                if scores[best][2] < scores[i][2]:
                    best = i

    if depth == 0:
        print()
        print(depth, scores)
        print()
                

    return scores[best] 

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

def randomCard(status):
        cards = []
        for i in range(len(status['decks']['player'])):
            if status['decks']['player'][i]['values'] is not None:
                cards.append(status['decks']['player'][i]['values'])
        for y in range(len(status['board'])):
            for x in range(len(status['board'][y])):
                if status['board'][y][x]['values'] is not None:
                    cards.append(status['board'][y][x]['values'])
        index = random.randrange(len(cards))
        return cards[index].copy()

def createPlayData(status):
    board = np.empty(3, dtype=object)
    for y in range(len(board)):
        board[y] = np.empty(3, dtype=object)

    newStatus = {
        'rules': status['rules'],
        'decks': {
            'player': [None] * 5,
            'enemy': [None] * 5
        }, 
        'board': [
            [None] * 3,
            [None] * 3,
            [None] * 3
        ]
    }

    for i in range(len(status['board'])):
        for j in range(len(status['board'][i])):
            newStatus['board'][i][j] = {
                'values': status['board'][i][j]['values']
            }

            if newStatus['board'][i][j]['values'] is not None:
                newStatus['board'][i][j]['owner'] = status['board'][i][j]['owner']
    for key in status['decks']:
        for i in range(len(status['decks'][key])):
            if key == 'player':
                newStatus['decks'][key][i] = {
                    'values': status['decks'][key][i]['values'],
                    'active': status['decks'][key][i]['active']
                }
            else:
                newStatus['decks'][key][i] = {
                    'values': status['decks'][key][i]['values'],
                    'hidden': status['decks'][key][i]['hidden']
                }

                if newStatus['decks'][key][i]['hidden']:
                    newStatus['decks'][key][i]['values'] = randomCard(status)
    return newStatus


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


#Main Loop (cancel with ctrl+c)
yourTurnLast = False
while True:
    if args.local: 
        fullScreen = loadImg('inputs/local3.png')
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
    yourTurnCrop = playWindow[35:55, 35:55]
    if yourTurnCrop.shape[0] < 20 or yourTurnCrop.shape[1] < 20:
        time.sleep(1)
        continue
    yourTurn = cv2.cvtColor(yourTurnCrop, cv2.COLOR_BGR2GRAY)
    if args.debug:
        saveImg('outputs', '03_yourTurn.png', yourTurn)

    errorL2 = cv2.norm(yourTurn, yourTurnTemplate, cv2.NORM_L2)
    similarity = 1 - errorL2 / (20 * 20)

    if similarity < 0:
        yourTurnLast = False
        time.sleep(1)
        continue
    else:
        if not yourTurnLast:
            yourTurnLast = True
            time.sleep(0.1)
            continue
    yourTurnLast = False
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

    #Setting up data structures
    decks = {
        'player': [None] * 5,
        'enemy': [None] * 5
    }
    board = [
        [None] * 3,
        [None] * 3,
        [None] * 3
    ]

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

    if args.debug:
        with open('outputs/' + str(roundCounter) + '/03_values.json', 'w') as f:
            f.write(json.dumps(status, default=lambda o: o.tolist()))

    status2 = createPlayData(status)

    if args.debug:
        with open('outputs/' + str(roundCounter) + '/04_playData.json', 'w') as f:
            f.write(json.dumps(status2))

    emptyBoardSpaces = 0
    for i in range(len(status2['board'])):
        for j in range(len(status2['board'][i])):
            if status2['board'][i][j]['values'] is None:
                emptyBoardSpaces += 1
    
    # variableDepth = 3 + (abs(9 - emptyBoardSpaces) / 2)
    # print('Starting solver with maxDepth=', variableDepth)
    move = minmax(status2['board'], status2['decks'], 'player', 0, 3, rules)

    print(move)

    if not args.local:
        cardPos = status['decks']['player'][move[0][0]]['position']
        boardPos = status['board'][move[0][2]][move[0][1]]['position']
        pyautogui.moveTo(top_left[0] + cardPos['x'] + (cardSize[0] / 2), top_left[1] + cardPos['y'] + (cardSize[1] / 2))
        pyautogui.click()
        pyautogui.moveTo(top_left[0] + boardPos['x'] + (cardSize[0] / 2), top_left[1] + boardPos['y'] + (cardSize[1] / 2))
        pyautogui.click()
        pyautogui.moveTo(top_left[0], top_left[1])

    #Cleanup for next round
    
    time.sleep(2)
    roundCounter +=1
    if args.local:
        break


