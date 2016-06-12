#!/bin/env/python
#coding: utf-8

from pygame import *
from PodSixNet.Connection import ConnectionListener, connection
from sklearn.svm import LinearSVC
from datetime import datetime
from time import sleep

import numpy as np
import random
import sys

u"""Encampment game with Pygame
Pygame, PodSixNet, scikit-learnを用いたネットワーク対戦の陣取りゲームです。


使用しているライブラリ
---------------
* Pygame
* PodSixNet
* scikit-learn 

Version
---------------
* python 2.7.6
* Pygame 1.9.2 pre
* scikit-learn 0.15.0b

"""

__author__ = "Yoshihiro Tanaka"
__date__   = "18 Jul. 2014"

class Game(ConnectionListener):
    def Network_startgame(self, data):
        u"""相手playerを待ち、playerNumberを受け取る"""
        self.running=True
        self.playerNum=data["player"]
        print ("PlayerNumber: " + str(self.playerNum))
    
    def Network_getRoute(self, data):
        u"""相手のroute情報を取得する"""
        self.enemyRouteList = data["route"]
        self.enemyBombList = data["bomb"]

    def Network_whistle(self, data):
        u"""互いのデータを互いが受領したことを確認した後でwhistleを鳴らす"""
        self.start(grid, self.controllWorm(grid, 0))
        self.whistle = True

    def Network_disconnected(self, data):
        u"""Serverから切断された場合の処理"""
        print("Server disconnected")
        exit()
     
    def __init__(self, grid):
        
        
        # DEFINE: flag
        self.flagSend     = True
        self.computerFlag = True
        self.first        = True
        self.whistle      = False
        self.once         = False
        self.running      = False
        self.winFlag      = 0
   
        # DEFINE: display size
        self.SCREEN_WIDTH  = (GRID_N * self.width) + ((GRID_N + 1) * self.margin)
        self.GRID_BOTTOM   = (GRID_N * self.height) + ((GRID_N + 1) * self.margin)
        self.SCREEN_HEIGHT  = self.GRID_BOTTOM + self.nav_bar + (self.margin * 2)
        self.width   = 30
        self.height  = 30
        self.margin  = 5
        self.nav_bar = 40

        # DEFINE: number of grids
        GRID_N = 15

        # DEFINE: font
        sysfont           = font.SysFont(None, 80)
        titlefont         = font.SysFont(None, 60)
        descfont          = font.SysFont(None, 25)
        startfont         = font.SysFont(None, 30)
        self.messagefont  = font.SysFont(None, 25)
        self.message1font = font.SysFont(None, 25)
        self.message2font = font.SysFont(None, 25)
        self.message3font = font.SysFont(None, 25)
        self.infofont     = font.SysFont(None, 22)

        # DEFINE: text
        self.win_text   = sysfont.render("- You WIN -", False, (0, 0, 0))
        self.lose_text  = sysfont.render("- You LOSE -", False, (0, 0, 0))
        self.draw_text  = sysfont.render("- DRAW -", False, (0, 0, 0))
        self.titleText  = titlefont.render("Description", False, (0, 0, 0))
        self.descText01 = descfont.render("key UP: Worm moves upward direction.", False, (0, 0, 0))
        self.descText02 = descfont.render("key DOWN: Worm moves downward direction.", False, (0, 0, 0))
        self.descText03 = descfont.render("key LEFT: Worm moves to the left direction.", False, (0, 0, 0))
        self.descText04 = descfont.render("key RIGHT: Worm moves to the right direction.", False, (0, 0, 0))
        self.descText05 = descfont.render("key R: Determine the route of the warm.", False, (0, 0, 0))
        self.descText06 = descfont.render("MOUSEDOWN: Place the bomb.", False, (0, 0, 0))
        self.descText07 = descfont.render("Press the SPACE key to start.", False, (0, 0, 0))

        
        # DEFINE: color
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

        # DEFINE: location of the positon
        self.firstList  = [[[7, 2], [7, 1]]]
        self.secondList = [[[7, 12], [7, 13]]]
        self.bombList   = []

        self.setField(grid)
        self.setPlayer(grid, 0)

        # DEFINE: count
        self.mouseCount = 0
        self.keyCount    = 0
       
        # DEFINE: resources
        self.bomb_icon = image.load("resources/bomb_icon.gif")
        self.bomb_exp = image.load("resources/bomb.png")
        self.bomb_icon = transform.scale(self.bomb_icon, (self.width, self.height))
        self.bomb_exp = transform.scale(self.bomb_exp, (self.width, self.height))
        self.set_bomb  = mixer.Sound("resources/set_bomb.wav")
        self.bomb  = mixer.Sound("resources/bomb_exp.wav")
        self.set_bomb.set_volume(0.20)
        self.bomb.set_volume(0.20)

        
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
            print "ex.", "localhost:31425"
            exit()
        print "Game client started"

        # Trueでloopから抜ける
        while not self.running:
            connection.Pump()
            self.Pump()
            sleep(0.01)
    
    def wait_keypress(self, grid):
        u"""キー入力を待つ"""
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
                    pass
                else:
                    self.getGridClick(grid)
                    self.mouseCount += 1

                    self.setInfo(0)
            elif ev.type == KEYDOWN:
                if ev.key == K_UP:
                    if self.keyCount >= 40:
                        pass
                    else:
                        print("Key: UP")
                        self.controllWorm(grid, 1)
                        self.keyCount += 1
                elif ev.key == K_DOWN:
                    if self.keyCount >= 40:
                        pass
                    else:
                        print("Key: DOWN")
                        self.controllWorm(grid, 2)
                        self.keyCount += 1
                elif ev.key == K_LEFT:
                    if self.keyCount >= 40:
                        pass
                    else:
                        print("Key: LEFT")
                        self.controllWorm(grid, 3)
                        self.keyCount += 1
                elif ev.key == K_RIGHT:
                    if self.keyCount >= 40:
                        pass
                    else:
                        print("Key: RIGHT")
                        self.controllWorm(grid, 4)
                        self.keyCount += 1
                elif ev.key == K_r:
                    self.setInfo(3)
                    self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
                elif ev.key == K_q:
                    print("Computer")
                    while self.computerFlag:
                        self.Computer()
                self.setInfo(0)

    def drawGrid(self, grid):
        u"""15x15のgridを描画する"""
        width  = self.width
        height = self.height
        margin = self.margin
        self.screen = display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        
        self.screen.fill(self.colorList[0])

        for row in range(15):
            for column in range(15):
                flag = False
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
                elif grid[row][column] == 8 or grid[row][column] == 9:
                    color = self.colorList[1]
                    draw.rect(self.screen, color, [(margin + width) * column + margin, (margin + height) * row + margin, width, height])
                    self.screen.blit(self.bomb_icon, ((margin + width) * column + margin, (margin + height) * row + margin))
                    flag = True

                if not flag:
                    draw.rect(self.screen, color, [(margin + width) * column + margin, (margin + height) * row + margin, width, height])
        
        self.drawNav()
        display.flip()

    def drawNav(self):
        u"""navigation barの上端と下端を描画する"""
        draw.rect(self.screen, self.colorList[1], [0, self.GRID_BOTTOM, self.SCREEN_WIDTH, self.margin])
        draw.rect(self.screen, self.colorList[1], [0, self.SCREEN_HEIGHT - self.margin, self.SCREEN_WIDTH, self.margin])

    def setField(self, grid):
        u"""陣を描画する"""
        grid[0][0]  = 7
        grid[14][0] = 7

        grid[0][14] = 6
        grid[14][14] = 6
        self.drawGrid(grid)

    def setPlayer(self, grid, player):
        u"""wormを初期位置に描画する"""
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
        u"""navigation barに表示する情報の描画を行う"""
        if number == 4:
            self.mouseCount = 5
            self.keyCount = 40
            self.number = number

        self.mouseInfo = self.infofont.render("Set bomb: " + str(5 - self.mouseCount), False, (0, 0, 0))
        self.keyInfo = self.infofont.render("Move worm: " + str(40 - self.keyCount), False, (0, 0, 0))
        if self.keyCount == 30:
            self.number = 2
        elif self.keyCount == 40:
            self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
        else:
            self.number = number
        draw.rect(self.screen, self.colorList[0], [0, self.GRID_BOTTOM + self.margin, 140, self.SCREEN_HEIGHT])
        
        self.screen.blit(self.mouseInfo, (10, self.GRID_BOTTOM + 10))
        self.screen.blit(self.keyInfo, (10, self.GRID_BOTTOM + 25))
        
  
        draw.rect(self.screen, self.colorList[0], [140, self.GRID_BOTTOM + self.margin, self.SCREEN_WIDTH, self.SCREEN_HEIGHT])
        self.drawNav()

        # 該当するメッセージが無い場合は表示しない(Errorとしてpassする)
        try:
            self.setMessage(self.number)
        except Exception as e:
            print("Message Error")
            print("message: " + str(e.message))
            print("e: " + str(e))

        
        display.flip()

    def setMessage(self, number):
        u"""messageを取得して描画する"""
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
            if not self.once:
                self.message = self.setPredictionMessage()
                self.once = True
        
        number = 0
        render = self.messagefont.render(self.message, False, self.fontcolor)
        self.screen.blit(render, (140, self.GRID_BOTTOM + 20))

    def setPredictionMessage(self):
        u"""学習によって得られた勝敗予測の結果を取得してtextで返す"""
        fontcolor = self.fontcolor
        prediction = self.judgeBySVM()
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
        u"""gameのstart時に表示するメッセージを起動時間に応じて変更する"""
        fontcolor = self.fontcolor
        playtime = int(datetime.now().strftime("%H"))


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
        u"""wormの移動可能ターンが10を切った時に表示するメッセージを返す"""
        self.limitText = "I soon became tired."

        return self.limitText

    def setWaitMessage(self):
        u"""相手を待つ間表示されるメッセージを返す"""
        self.waitText = "He will blow hot and cold."

        return self.waitText

    def getGridClick(self, grid):
        u"""clickされたgridのpositionを取得する"""
        pos = mouse.get_pos()
        row = pos[1] // (self.height + self.margin)
        column = pos[0] // (self.width + self.margin) 
        # gridの範囲外をclickした時のErrorをpassする
        try:
            grid[row][column] = 8
            self.set_bomb.play(0)
        except:
            pass
        self.drawGrid(grid)
        self.bombList.append([row, column])

    def controllWorm(self, grid, move):
        u"""押されたキーに応じてwormの描画を更新する"""
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
        u"""ゲームの再生を行う"""
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
                            self.bomb.play(0)
                            break

                        row    = playersList[j][k][i][0]
                        column = playersList[j][k][i][1]
                        grid[row][column] = playerColorList[j]

                        if i == 0:
                            # bombへのhit判定 --->
                            for n in bombList:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 1:
                                            grid[row][column] = 9
                                            grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0
                                            playersList[1] = []
                                            BOMB = True

                            for n in enemyBombList:
                                if row == n[0]:
                                    if column == n[1]:
                                        if j == 0:
                                            grid[row][column] = 9
                                            grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0
                                            playersList[0] = []
                                            BOMB = True
                            # <---

                            # 勝利判定 --->
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
                            # <---
                    if not BOMB:
                        grid[playersList[j][k - 1][1][0]][playersList[j][k - 1][1][1]] = 0

                    BOMB = False

                    sleep(0.3)
                    self.drawGrid(grid)
                    self.setInfo(0)
                else:
                    pass
            sleep(0.3)
        self.outputTSV(2)
        self.Judge(2)


    def outputTSV(self, result):
        u"""データを加工してtsvファイルを出力する"""
        wormRoute = self.controllWorm(grid, 0)
        bombPos  = self.bombList
        outputRow    = open("row.tsv", "a")
        outputColumn = open("column.tsv", "a")
        outputBomb   = open("bomb.tsv", "a")
        rowList = []
        columnList = []
        bombList = []

        outputRow.write(str(result))
        outputColumn.write(str(result))
        outputBomb.write(str(result))

        for j in range(len(wormRoute)):
            for k in range(len(wormRoute[j])):
                for i in range(len(wormRoute[j][k])):
                    if k == 0:
                        rowList.append(wormRoute[j][k][0])
                        columnList.append(wormRoute[j][k][1])

        for i in bombPos:
            bombList.append(i[0])
            bombList.append(i[1])

        gridList = [rowList, columnList]

        for i in range(len(gridList)):
            if len(gridList[i]) >= 0 and len(gridList[i]) < 40:
                while len(gridList[i]) < 40:
                    gridList[i].append(0)
            elif len(gridList[i]) > 40:
                while len(gridList[i]) > 40:
                    gridList[i].pop()

        if len(bombList) >= 0 and len(bombList) < 10:
            while len(bombList) < 10:
                bombList.append(0)
        elif len(bombList) > 10:
            while len(bombList) > 10:
                bombList.pop()


        for i in rowList:
            outputRow.write("\t" + str(i))
        for i in columnList:
            outputColumn.write("\t" + str(i))
        for i in bombList:
            outputBomb.write("\t" + str(i))

        outputRow.write("\n")
        outputColumn.write("\n")
        outputBomb.write("\n")
        
        outputRow.close()
        outputColumn.close()
        outputBomb.close()


    def refresh(self, grid):
        u"""全てrefreshする"""
        for row in range(15):
            for column in range(15):
                grid[row][column] = 1

        self.drawGrid(grid)

    def Judge(self, result):
        u"""勝敗の結果を描画する"""
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
            if ev.type == QUIT:
                quit()
            elif ev.type == KEYDOWN:      
                if ev.key == K_ESCAPE:
                    quit()

    def White(self):
        u"""指定範囲をWhiteで塗りつぶす"""
        color = self.colorList[0]
        draw.rect(self.screen, color, [0, self.SCREEN_HEIGHT / 4, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2])

    def startupScreen(self, grid):
        u"""説明を描画する"""
        if self.first:

            self.White()
            self.screen.blit(self.titleText,  (50,  (self.SCREEN_HEIGHT / 4) + 10))
            self.screen.blit(self.descText01, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 0)))
            self.screen.blit(self.descText02, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 1)))
            self.screen.blit(self.descText03, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 2)))
            self.screen.blit(self.descText04, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 3)))
            self.screen.blit(self.descText05, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 4)))
            self.screen.blit(self.descText06, (70,  (self.SCREEN_HEIGHT / 4) + 65 + (25 * 5)))
            self.screen.blit(self.descText07, (100, (self.SCREEN_HEIGHT / 4) + 230))

            display.flip()
            self.first = False

        while True:
            ev = event.wait()
            if ev.type == QUIT:
                quit()
            elif ev.type == KEYDOWN:
                if ev.key == K_SPACE:
                    self.setField(grid)
                    self.setPlayer(grid, 0)
                    self.setInfo(1)
                    self.wait_keypress(grid)

    def judgeBySVM(self):
        u"""SVCを用いてtsvデータから学習し、routeデータから勝敗を予測する"""
        routeData  = self.controllWorm(grid, 0)
        label      = []
        data       = []
        data_tmp   = []
        dataList   = []
        rowList    = []
        columnList = []
        predList   = []

        training_row    = np.loadtxt('row.tsv', delimiter='\t')
        training_column = np.loadtxt('column.tsv', delimiter='\t')
        training_bomb   = np.loadtxt('bomb.tsv', delimiter='\t')
        trainingList    = [training_row, training_column]

        for j in range(len(routeData)):
            for k in range(len(routeData[j])):
                for i in range(len(routeData[j][k])):
                    if k == 0:
                        rowList.append(routeData[j][k][0])
                        columnList.append(routeData[j][k][1])

        for l in range(len(trainingList)):
            label    = []
            data     = []
            data_tmp = []
            dataList = []

            for k in range(len(trainingList[l])):
                for i in range(len(trainingList[l][k])):
                    if i == 0:
                        label.append(int(trainingList[l][k][0]))
                        if k != 0:
                            data.append(data_tmp)
                        data_tmp = []
                    else:
                        data_tmp.append(trainingList[l][k][i])
            data.append(data_tmp)

            # TODO: Grid search
            # URL : http://sucrose.hatenablog.com/entry/2013/05/25/133021
            estimator = LinearSVC()#C=1.0)
            estimator.fit(data, label)

            if l == 0 or l == 1:
                if l == 0:
                    dataList = rowList
                elif l == 1:
                    dataList = columnList

                if len(dataList) >= 0 and len(dataList) < 40:
                    while len(dataList) < 40:
                        dataList.append(0)
                elif len(dataList) > 40:
                    while len(dataList) > 40:
                        dataList.pop()

            prediction = estimator.predict(dataList)
            predList.append(prediction[0])


        if predList[0] == 0 and predList[0] == 0:
            prediction = [0]
        elif predList[0] == 1 and predList[0] == 1:
            prediction = [1]
        elif predList[0] == 2 and predList[0] == 2:
            prediction = [2]
        elif predList[0] == 0:
            prediction = [0]
        elif predList[0] == 1:
            prediction = [1]
        elif predList[0] == 2:
            prediction = [2]

        return prediction

    def Computer(self):
        u"""computerの動きを制御する"""
        routeData       = self.controllWorm(grid, 0)
        bombPos         = self.bombList

        training_row    = np.loadtxt('row.tsv', delimiter='\t')
        training_column = np.loadtxt('column.tsv', delimiter='\t')
        training_bomb   = np.loadtxt('bomb.tsv', delimiter='\t')

        trainingList    = [training_row, training_column]

        # prediction: [row01, row02, column01, column02]
        # up down left right
        predList     = []
        row00List    = []
        column00List = []       
        row01List    = []
        column01List = []
        row02List    = []
        column02List = []
        bombList     = []
        shuffleList  = []

        if self.playerNum == 0:
            if (routeData[-1][0][0] == 0 and routeData[-1][0][1] == 14) or (routeData[-1][0][0] == 14 and routeData[-1][0][1] == 14):
                self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
                self.computerFlag = False
        elif self.playerNum == 1:
            if (routeData[-1][0][0] == 0 and routeData[-1][0][1] == 0) or (routeData[-1][0][0] == 14 and routeData[-1][0][1] == 0):
                self.Send({"action": "getRoute", "route": self.controllWorm(grid, 0), "bomb": self.bombList, "player": self.playerNum})
                self.computerFlag = False

        for j in range(len(routeData)):
            for k in range(len(routeData[j])):
                for i in range(len(routeData[j][k])):
                    if k == 0:
                        row00List.append(routeData[j][k][0])
                        row01List.append(routeData[j][k][0])
                        row02List.append(routeData[j][k][0])
                        column00List.append(routeData[j][k][1])
                        column01List.append(routeData[j][k][1])
                        column02List.append(routeData[j][k][1])

        row01List.append(row01List[-1] - 1)
        row02List.append(row02List[-1] + 1)
        column01List.append(column01List[-1] - 1)
        column02List.append(column02List[-1] + 1)

        rowList = [row01List, row02List]
        columnList = [column01List, column02List]
        
        for l in range(len(trainingList)):
            label = []
            data  = []
            data_tmp = []
            dataList = []

            for k in range(len(trainingList[l])):
                for i in range(len(trainingList[l][k])):
                    if i == 0:
                        label.append(int(trainingList[l][k][0]))
                        if k != 0:
                            data.append(data_tmp)
                        data_tmp = []
                    else:
                        data_tmp.append(trainingList[l][k][i])
            data.append(data_tmp)

            estimator = LinearSVC(C=1.0)
            estimator.fit(data, label)

            if l == 0 or l == 1:
                if l == 0:
                    dataList = rowList
                elif l == 1:
                    dataList = columnList

                # WARN:
                # 座標データ数が0以上40以下であった場合、40に整形する
                for i in dataList:
                    if len(i) >= 0 and len(i) < 40:
                        while len(i) < 40:
                            i.append(0)
                    elif len(i) > 40:
                        while len(i) > 40:
                            i.pop()

            if l == 0:
                for i in dataList:
                    prediction = estimator.predict(i)
                    predList.append(prediction[0])
            elif l == 1:
                for i in dataList:
                    prediction = estimator.predict(i)
                    predList.append(prediction[0])

        # WARN: 
        if 1 in predList:
            for i in range(len(predList)):
                if predList[i] == 1:
                    shuffleList.append(i)

            random.shuffle(shuffleList)
        elif 2 in predList:
            for i in range(len(predList)):
                if predList[i] == 2:
                    shuffleList.append(i)

            random.shuffle(shuffleList)
        else:
            shuffleList.append(random.randint(0, 3))

        self.controllWorm(grid, shuffleList[0] + 1)
        sleep(0.5)

if __name__=='__main__':

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
            quit()
        else:
            game.startupScreen(grid)
