# -*- coding: utf-8 -*-

from round import Round
from player import Player

blinds = [10, 20, 30, 50, 80, 100, 120, 160, 200, 300, 400, 500]

# returns the index for the next round's button
def nextPlayer(button, length):
    return (button + 1) % length

# from 10 to 10 rounds, the blinds get bigger
def getBlinds(roundNumber):
    length = len(blinds)
    if (roundNumber // 10 < length):
        return blinds[roundNumber // 10]
    else:
        return blinds[len(blinds) - 1]
    
# a game consists of players, who is the button, round number and the
# simulation of rounds until one player is not bankrupt
class Game:
    
    def __init__(self, noPlayers):
        self.roundNumber = 1
        self.button = 0
        self.players = []
        for i in range(noPlayers):
            self.players.append(Player())
    
    def resetPlayersStats(self):
        for pl in self.players:
             pl.roundCoins = 0
             pl.inGame = True
    
    def totalMoney(self):
        return len(self.players) * 1000

    
    def getOnePlayerStats(self, onePlayer):
        res = []
        res.append(onePlayer.averageWinnings(self.totalMoney()))
        res.append(onePlayer.winningPercentage(self.roundNumber))
        res.append(onePlayer.flopWinPercentage())
        res.append(onePlayer.turnWinPercentage())
        res.append(onePlayer.riverWinPercentage())
        res.append(onePlayer.cardsOnWinPercentage())
        res.append(onePlayer.agresiveness())
        res.append(onePlayer.flopPerRounds(self.roundNumber))
        res.append(onePlayer.turnPerRounds(self.roundNumber))
        res.append(onePlayer.riverPerRounds(self.roundNumber))
        res.append(onePlayer.cardsOnPerRounds(self.roundNumber))
        return res
        
    def updatePlayersStats(self):
        res = []
        for plr in self.players:
            res.append(self.getOnePlayerStats(plr))
        return res
    
    def playGame(self):
        while len(self.players) > 1:
            blind = getBlinds(self.roundNumber)
            print('blinds ' , blind)
            statsList = self.updatePlayersStats()
            rnd = Round(blind, self.players, self.button, statsList)
            self.players = rnd.roundProcess()
            self.resetPlayersStats()
            self.button = nextPlayer(self.button, len(self.players))
            self.roundNumber += 1
            if self.roundNumber % 3 == 0:
                for row in statsList:
                    print(row)
        

# how to start the game
game = Game(3)
game.playGame()
