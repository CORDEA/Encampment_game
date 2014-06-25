#!/bin/env/python
#coding: utf-8

from PodSixNet.Connection import ConnectionListener, connection
from sklearn.svm import LinearSVC
import numpy as np
from datetime import datetime

class Game(ConnectionListener):
    def Network_startgame(self, data):
        self.running=True
        self.playerNum=data["player"]
        print ("PlayerNumber: " + str(self.playerNum))
    
    def Network_getRoute(self, data):
        self.enemyRouteList = data["route"]
        self.enemyBombList = data["bomb"]
        print(self.enemyRouteList)
        print(self.playerNum)
        print(len(self.enemyRouteList))

    def Network_whistle(self, data):
        self.start(grid, self.controllWorm(grid, 0))
        self.whistle = True

    def Network_disconnected(self, data):
        print("Server disconnected")
        exit()
     
    def __init__(self, grid):
        
        # Define number of grids
        GRID_N = 15
        
        self.width  = 30
        self.height = 30
        self.margin = 5
        self.nav_bar = 40


        self.flagSend = True
        self.first = True
        self.whistle = False

       
        # Define some colors, display size
        self.SCREEN_WIDTH  = (GRID_N * self.width) + ((GRID_N + 1) * self.margin)
        self.GRID_BOTTOM   = (GRID_N * self.height) + ((GRID_N + 1) * self.margin)
        self.SCREEN_HEIGHT  = self.GRID_BOTTOM + self.nav_bar + (self.margin * 2)

        sysfont = font.SysFont(None, 80)
        self.win_text = sysfont.render("- You WIN -", False, (0, 0, 0))
        self.lose_text = sysfont.render("- You LOSE -", False, (0, 0, 0))
        self.draw_text = sysfont.render("- DRAW -", False, (0, 0, 0))

        titlefont = font.SysFont(None, 60)
        descfont = font.SysFont(None, 25)
        startfont = font.SysFont(None, 30)
        self.messagefont = font.SysFont(None, 25)
        self.message1font = font.SysFont(None, 25)
        self.message2font = font.SysFont(None, 25)
        self.message3font = font.SysFont(None, 25)
        self.infofont = font.SysFont(None, 22)
        self.titleText = titlefont.render("Description", False, (0, 0, 0))
        self.descText01 = descfont.render("key UP: Worm moves upward direction.", False, (0, 0, 0))
        self.descText02 = descfont.render("key DOWN: Worm moves downward direction.", False, (0, 0, 0))
        self.descText03 = descfont.render("key LEFT: Worm moves to the left direction.", False, (0, 0, 0))
        self.descText04 = descfont.render("key RIGHT: Worm moves to the right direction.", False, (0, 0, 0))
        self.descText05 = descfont.render("key R: Determine the route of the warm.", False, (0, 0, 0))
        self.descText06 = descfont.render("MOUSEDOWN: Place the bomb.", False, (0, 0, 0))
        self.descText07 = descfont.render("Press the SPACE key to start.", False, (0, 0, 0))

        self.winFlag = 0
   
        self.colorList = [
                (255, 255, 255),
                (  0,   0,   0), 
                (255,   0,   0),
                (  0, 255,   0),
                (  0,   0, 255),
                (255, 165,   0),
                (  0, 180,   0),
                (180,   0,   0)]

        # WHITE  = (255, 255, 255)
        # BLACK  = (  0,   0,   0)
        # RED    = (255,   0,   0)
        # GREEN  = (  0, 255,   0)
        # BLUE   = (  0,   0, 255)
        # YELLOW = (255, 255,   0)
        # ORANGE = (255, 165,   0)
        # DARK GREEN = (  0, 100,   0)


        self.fontcolor = self.colorList[1]

        self.firstList  = [[[7, 2], [7, 1]]]
        self.secondList = [[[7, 12], [7, 13]]]
        self.bombList   = []
        self.setField(grid)
        self.setPlayer(grid, 0)

        self.mouseCount = 0
        self.keyCount    = 0
        
        
        self.running = False
        address=raw_input("Host:Port : ")
        try:
            if not address:
                host, port = "localhost", 8000
            else:
                host,port = address.split(":")
                self.Connect((host, int(port)))
        except:
            print "Error Connecting to Server"
            print "Usage:", "host:port"
            print "e.g.", "localhost:31425"
            exit()
        print "Game client started"
        while not self.running:
            connection.Pump()
            self.Pump()
            sleep(0.01)
    
    def wait_keypress(self, grid):
        while True:
            connection.Pump()
            self.Pump()
            sleep(0.0001)

            try:
                enemyRouteList = self.enemyRouteList
                enemyBombList  = self.enemyBombList
                if self.flagSend:
                    self.Send({"action": "getStartFlag", "start": True, "player": self.playerNum})
                    self.flagSend = False
                #if len(enemyRouteList) == 1:
                #    self.wait_keypress(grid)
            except:
                pass

            ev   = event.wait()
            if ev.type == QUIT:
                quit()
            elif ev.type == MOUSEBUTTONDOWN:
                if self.mouseCount >= 5:
                    print("BOMB LIMIT")
                else:
                    print("MOUSE BUTTON DOWN")
                    self.getGridClick(grid)
                    self.mouseCount += 1

                    self.setInfo(0)
            elif ev.type == KEYDOWN:
                if ev.key == K_UP:
                    if self.keyCount >= 40:
                        print("LIMIT")
                    else:
                        print("Key: UP")
                        self.controllWorm(grid, 1)
                        self.keyCount += 1
                elif ev.key == K_DOWN:
                    if self.keyCount >= 40:
                        print("LIMIT")
                    else:
                        print("Key: DOWN")
                        self.controllWorm(grid, 2)
                        self.keyCount += 1
                elif ev.key == K_LEFT:
                    if self.keyCount >= 40:
                        print("LIMIT")
                    else:
                        print("Key: LEFT")
                        self.controllWorm(grid, 3)
                        self.keyCount += 1
                elif ev.key == K_RIGHT:
                    if self.keyCount >= 40:
                        print("LIMIT")
                    else:
                        print("Key: RIGHT")
                        self.controllWorm(grid, 4)
                        self.keyCount += 1
                elif ev.key == K_r:
                    print("Send")
                    self.setInfo(3)
                    self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
                
                self.setInfo(0)

    def drawGrid(self, grid):
        width = self.width
        height = self.height
        margin = self.margin
        self.screen = display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        
        self.screen.fill(self.colorList[0])

        for row in range(15):
            for column in range(15):
                color = self.colorList[1]
                if grid[row][column] == 2:
                    color = self.colorList[2]
                elif grid[row][column] == 3:
                    color = self.colorList[3]
                elif grid[row][column] == 4:
                    color = self.colorList[4]
                elif grid[row][column] == 5:
                    color = self.colorList[5]
                elif grid[row][column] == 6:
                    color = self.colorList[6]
                elif grid[row][column] == 7:
                    color = self.colorList[7]
                draw.rect(self.screen, color, [(margin + width) * column + margin, (margin + height) * row + margin, width, height])
        
        self.drawNav()
        display.flip()

    def drawNav(self):
        draw.rect(self.screen, self.colorList[1], [0, self.GRID_BOTTOM, self.SCREEN_WIDTH, self.margin])
        draw.rect(self.screen, self.colorList[1], [0, self.SCREEN_HEIGHT - self.margin, self.SCREEN_WIDTH, self.margin])

    def setField(self, grid):
        grid[0][0]  = 7
        grid[14][0] = 7

        grid[0][14] = 6
        grid[14][14] = 6
        self.drawGrid(grid)

    def setPlayer(self, grid, player):
        if player == 0:
            grid[7][1] = 5
            grid[7][2] = 5

            grid[7][12] = 3
            grid[7][13] = 3
        elif player == 1:
            grid[7][12] = 3
            grid[7][13] = 3
        elif player == 2:
            grid[7][1] = 5
            grid[7][2] = 5
        self.drawGrid(grid)

    def setInfo(self, number):
        if number == 4:
            self.mouseCount = 5
            self.keyCount = 40

        self.mouseInfo = self.infofont.render("Set bomb: " + str(5 - self.mouseCount), False, (0, 0, 0))
        self.keyInfo = self.infofont.render("Move worm: " + str(40 - self.keyCount), False, (0, 0, 0))
        if self.keyCount == 20:
            self.number = 2
        elif self.keyCount == 40:
            self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
        else:
            self.number = number
        draw.rect(self.screen, self.colorList[0], [0, self.GRID_BOTTOM + self.margin, 140, self.SCREEN_HEIGHT - self.margin])
        
        self.screen.blit(self.mouseInfo, (10, self.GRID_BOTTOM + 10))
        self.screen.blit(self.keyInfo, (10, self.GRID_BOTTOM + 25))
        #try:
        draw.rect(self.screen, self.colorList[0], [140, self.GRID_BOTTOM + self.margin, self.SCREEN_WIDTH, self.SCREEN_HEIGHT - self.margin])
        self.setMessage(self.number)
        #except:
            #print("message not defined")
        
        display.flip()

    def setMessage(self, number):
        if self.playerNum == 0:
            self.fontcolor = self.colorList[5]
        elif self.playerNum == 1:
            self.fontcolor = self.colorList[3]

        if number == 1:
            self.message = self.setStartMessage()
        elif number == 2:
            self.message = self.setLimitMessage()
        elif number == 3:
            self.message = self.setWaitMessage()
        elif number == 4:
            self.message = self.setPredictionMessage()
        
        number = 0
        render = self.messagefont.render(self.message, False, self.fontcolor)
        self.screen.blit(render, (140, self.GRID_BOTTOM + 20))

    def setPredictionMessage(self):
        fontcolor = self.fontcolor
        prediction = self.judgeBySVM()
        print(prediction[0])
        if prediction[0] == 0:
            self.predText = "I stand no chance against him."
        elif prediction[0] == 1:
            self.predText = "I'm sure you can win this game."
        elif prediction[0] == 2:
            self.predText = "This game is a tie, isn't it?"
        else:
            self.predText = "I'm not sure of winning the game this time."

        return self.predText

    def setStartMessage(self):
        fontcolor = self.fontcolor
        playtime = int(datetime.now().strftime("%H"))

        print playtime

        if playtime >= 0 and playtime <= 5:
            self.timeText = "You work far into the night. Are you still awake?"
        elif playtime >= 6 and playtime <= 9:
            self.timeText = "Good morning, my partner."
        elif playtime >= 9 and playtime <= 11:
            self.timeText = "Hello there! I'm hungry but how about you?"
        elif playtime >= 12 and playtime <= 14:
            self.timeText = "Hello. I'm full and sleepy."
        elif playtime == 15:
            self.timeText = "Good afternoon. Did you buy snacks?"
        elif playtime >= 16 and playtime <= 20:
            self.timeText = "Good evening, my partner."
        elif playtime >= 21 and playtime <= 23:
            self.timeText = "Good evening. What do you want to eat for dinner?"

        return self.timeText

    def setLimitMessage(self):
        self.limitText = "I soon became tired."

        return self.limitText

    def setWaitMessage(self):
        self.waitText = "He will blow hot and cold."

        return self.waitText

    def getGridClick(self, grid):
        pos = mouse.get_pos()
        print(pos)
        row = pos[1] // (self.height + self.margin)
        column = pos[0] // (self.width + self.margin) 
        grid[row][column] = 2
        self.drawGrid(grid)
        self.bombList.append([row, column])
        print(str(pos) + " " + str(row) + " " + str(column))

    def controllWorm(self, grid, move):
        global isCollision
        playerNum = self.playerNum
        if playerNum == 0:
            ownList = self.firstList
            playerColor = 5
            player = 1
        elif playerNum == 1:
            ownList = self.secondList
            playerColor = 3
            player = 2
        else:
            print("Unexpexted Error")

        headList = []
        tailList = []

        if (move == 0):
            return ownList
        elif (move == 1):
            if ownList[-1][0][0] == 0:
                row    = ownList[-1][0][0]
                isCollision[0] += 1
                for i in range(1, 4):
                    isCollision[i] = 0
            else:
                row    = ownList[-1][0][0] - 1
                for i in range(len(isCollision)):
                    isCollision[i] = 0
            column = ownList[-1][0][1]
        elif (move == 2):
            if ownList[-1][0][0] == 14:
                row    = ownList[-1][0][0]
                isCollision[1] += 1
                isCollision[0] = 0
                for i in range(2, 4):
                    isCollision[i] = 0
            else:
                row    = ownList[-1][0][0] + 1
                for i in range(len(isCollision)):
                    isCollision[i] = 0
            column = ownList[-1][0][1]
        elif (move == 3):
            row    = ownList[-1][0][0]
            if ownList[-1][0][1] == 0:
                column = ownList[-1][0][1]
                isCollision[2] += 1
                for i in range(0, 2):
                    isCollision[i] = 0
                isCollision[3] = 0
            else:
                column = ownList[-1][0][1] - 1
                for i in range(len(isCollision)):
                    isCollision[i] = 0
        elif (move == 4):    
            row    = ownList[-1][0][0]
            if ownList[-1][0][1] == 14:
                column = ownList[-1][0][1]
                for i in range(3):
                    isCollision[i] = 0
                isCollision[3] += 1
            else:
                column = ownList[-1][0][1] + 1
                for i in range(len(isCollision)):
                    isCollision[i] = 0
        
        grid[row][column] = playerColor
        headList.append(row)
        headList.append(column)
            
        row    = ownList[-1][0][0]
        column = ownList[-1][0][1]
        grid[row][column] = playerColor
        tailList.append(row)
        tailList.append(column)

        grid[ownList[-1][1][0]][ownList[-1][1][1]] = 0
        print(isCollision)

        for i in range(len(isCollision)):
            if isCollision[i] > 1:
                grid[ownList[-1][1][0]][ownList[-1][1][1]] = playerColor

            #grid[ownList[-1][1][0]][ownList[-1][1][1]] = 0
            #isCollision = 0

        ownList.append([headList, tailList])

        self.setField(grid)
        self.setPlayer(grid, player)
        self.drawGrid(grid)

    def start(self, grid, ownList):
        enemyRouteList = self.enemyRouteList
        enemyBombList  = self.enemyBombList
        bombList = self.bombList

        playerNum = self.playerNum
        if playerNum == 0:
            yourArea = [[0, 0], [14, 0]]
            enemyArea = [[0, 14], [14, 14]]
            playerColorList = [5, 3]
        elif playerNum == 1:
            yourArea = [[0, 14], [14, 14]]
            enemyArea = [[0, 0], [14, 0]]
            playerColorList = [3, 5]
        else:
            print("Unexpexted Error")

        print("Your : " + str(ownList))
        #print("Player02: " + str(enemyRouteList))
        playersList = [ownList, enemyRouteList]
        self.refresh(grid)
        sleep(1.0)
        self.setField(grid)
        self.setPlayer(grid, 0)
        self.setInfo(4)

        if len(playersList[0]) >= len(playersList[1]):
            length = len(playersList[0])
        else:
            length = len(playersList[1])

        row = 0
        column = 0
        BOMB = False
        game_continue = False
        drawFlag = [0, 0]

        for k in range(length):
            if drawFlag[0] == 1 and drawFlag[1] == 1:
                self.outputTSV(2)
                self.Judge(2)
            elif drawFlag[0] == 1 and drawFlag[1] == 0:
                self.outputTSV(1)
                self.Judge(1)
            elif drawFlag[1] == 1 and drawFlag[0] == 0:
                self.outputTSV(0)
                self.Judge(0)

            for j in range(2):
                if playersList[j][k:k + 1]:
                    for i in range(2):
                        if BOMB:
                            break

                        row    = playersList[j][k][i][0]
                        column = playersList[j][k][i][1]
                        grid[row][column] = playerColorList[j]

                        if i == 0:
                            for n in bombList:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 1:
                                            print("Enemy HIT")
                                            grid[row][column] = 2
                                            grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0
                                            playersList[1] = []
                                            BOMB = True

                            for n in enemyBombList:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 0:
                                            print("BOMB HIT")
                                            grid[row][column] = 2
                                            grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0
                                            playersList[0] = []
                                            BOMB = True

                            for n in yourArea:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 1:
                                            drawFlag[1] = 1

                            for n in enemyArea:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 0:
                                            drawFlag[0] = 1
                    
                    if not BOMB:
                        grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0

                    BOMB = False

                    sleep(0.3)
                    self.drawGrid(grid)
                    self.setInfo(0)
                else:
                    print("turn end")
                    pass
            sleep(0.3)
        self.outputTSV(2)
        self.Judge(2)


    def outputTSV(self, result):
        wormRoute = self.controllWorm(grid, 0)
        outputFile = open("output.tsv", "a")
        outputFile.write(str(result))
        for j in range(len(wormRoute)):
            for k in range(len(wormRoute[j])):
                for i in range(len(wormRoute[j][k])):
                    if k == 0:
                        outputFile.write("\t" + str(wormRoute[j][k][i]))
        outputFile.write("\n")
        outputFile.close()


    def refresh(self, grid):
        for row in range(15):
            for column in range(15):
                grid[row][column] = 1

        self.drawGrid(grid)

    def Judge(self, result):
        self.White()

        if result == 0:
            self.screen.blit(self.lose_text, (50, self.SCREEN_HEIGHT / 2))
        elif result == 1:
            self.screen.blit(self.win_text, (50, self.SCREEN_HEIGHT / 2))
        elif result == 2:
            self.screen.blit(self.draw_text, (50, self.SCREEN_HEIGHT / 2))

        self.Send({"action": "getEndFlag", "endPlayer": self.playerNum})

        display.flip()
        
        while True:
            ev   = event.wait()
            if ev.type == KEYDOWN:      
                if ev.key == K_ESCAPE:
                    quit()

    def White(self):
        color = self.colorList[0]
        draw.rect(self.screen, color, [0, self.SCREEN_HEIGHT / 4, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2])

    def startupScreen(self, grid):
        if self.first:

            self.White()
            self.screen.blit(self.titleText, (50, self.SCREEN_HEIGHT / 4 + 10))
            self.screen.blit(self.descText01, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 0)))
            self.screen.blit(self.descText02, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 1)))
            self.screen.blit(self.descText03, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 2)))
            self.screen.blit(self.descText04, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 3)))
            self.screen.blit(self.descText05, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 4)))
            self.screen.blit(self.descText06, (70, (self.SCREEN_HEIGHT / 4) + 65 + (25 * 5)))
            self.screen.blit(self.descText07, (100, (self.SCREEN_HEIGHT / 4) + 230))

            display.flip()
            self.first = False

        while True:
            ev = event.wait()
            if ev.type == KEYDOWN:
                if ev.key == K_SPACE:
                    print("game start")
                    self.setField(grid)
                    self.setPlayer(grid, 0)
                    self.setInfo(1)
                    self.wait_keypress(grid)

    def judgeBySVM(self):
        routeData = self.controllWorm(grid, 0)
        label = []
        data  = []
        data_tmp = []
        dataList = []

        data_training = np.loadtxt('output.tsv', delimiter='\t')

        for k in range(len(data_training)):
            for i in range(len(data_training[k])):
                if i == 0:
                    label.append(int(data_training[k][0]))
                    if k != 0:
                        data.append(data_tmp)
                    data_tmp = []
                else:
                    data_tmp.append(data_training[k][i])
        data.append(data_tmp)

        for j in range(len(routeData)):
            for k in range(len(routeData[j])):
                for i in range(len(routeData[j][k])):
                    if k == 0:
                        dataList.append(routeData[j][k][i])

        estimator = LinearSVC(C=1.0)
        estimator.fit(data, label)

        if len(dataList) >= 80:
            print("too much route")
            while len(dataList) == 80:
                dataList.pop()

        print("Input DATA: " + str(dataList))
        prediction = estimator.predict(dataList)
        return prediction

if __name__=='__main__':
    from time import sleep
    from pygame import *
    import sys

    init()
    isCollision = [0, 0, 0, 0]
    save = 0

    grid = []

    for row in range(15):
        grid.append([])
        for column in range(15):
            grid[row].append(0)
   
    game = Game(grid)
    
    while True:
        ev = event.wait()
        if ev.type == QUIT:
            break
        else:
            game.startupScreen(grid)
