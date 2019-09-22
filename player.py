# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# the game will be played in console, so i've made this function to make the
# game 'playable'. It display the cards on player hand or on table, more
# precise - the images of cards.Images are renamed to corespond to card numbers
def displayCards(hand):
    fig = plt.figure(figsize = (9, 3))
    columns = len(hand)
    rows = 1
    for i in range(1, columns +1):
        path = 'cards/' + str(hand[i - 1]) + '.jpg'
        img = mpimg.imread(path)
        fig.add_subplot(rows, columns, i)
        plt.axis('off')
        plt.imshow(img)
    plt.show()

# Player class describes players attributes and actions. A player has a hand
# some coins, coins invested in current round, it's not in game if he folds

class Player:
    
    def __init__(self):
        self.hand = []
        self.coins = 1000
        self.roundCoins = 0
        self.inGame = True
        self.called = False
        self.winnings = 0
        self.decisions = 0
        self.raiseFromCheck = 0
        self.reRaise = 0
        self.preFlopWins = 0
        self.flopWins = 0
        self.turnWins = 0
        self.riverWins = 0
        self.cardsOnWins = 0
        self.roundsWithFlop = 0
        self.roundsWithTurn = 0
        self.roundsWithRiver = 0
        self.roundsWithCardsOn = 0
        
    def getProps(self, otherPlayer):
        self.hand = otherPlayer.hand
        self.coins = otherPlayer.coins
        self.roundCoins = otherPlayer.roundCoins
        self.inGame = otherPlayer.inGame
        self.winnings = otherPlayer.winnings
        self.decisions = otherPlayer.decisions
        self.raiseFromCheck = otherPlayer.raiseFromCheck
        self.reRaise = otherPlayer.reRaise
        self.preFlopWins = otherPlayer.preFlopWins
        self.flopWins = otherPlayer.flopWins
        self.turnWins = otherPlayer.turnWins
        self.riverWins = otherPlayer.riverWins
        self.cardsOnWins = otherPlayer.cardsOnWins
        self.roundsWithFlop = otherPlayer.roundsWithFlop
        self.roundsWithTurn = otherPlayer.roundsWithTurn
        self.roundsWithRiver = otherPlayer.roundsWithRiver
        self.roundsWithCardsOn = otherPlayer.roundsWithCardsOn
        
    def extractBlind(self, money):
        if self.coins < money:
            self.coins = 0
            return self.coins
        else:
            self.coins = self.coins - money
            return money
        
    def receiveCard(self, card):
        self.hand.append(card)
        
    def isBankrupt(self):
        return self.coins == 0
    
    def allIn(self):
        return self.inGame == True and self.coins == 0
    
    def averageWinnings(self, totalMoney):
        totalWins = self.totalWinRounds()
        if totalWins > 0:
            return self.winnings / (totalWins * totalMoney) * 100
        else:
            return 0
    
    def totalWinRounds(self):
        totalWins = self.preFlopWins + self.flopWins + self.turnWins + \
                self.riverWins + self.cardsOnWins
        return totalWins
        
    def winningPercentage(self, rounds):
        return self.totalWinRounds() / rounds * 100 if rounds > 0 else 0
    
    def flopWinPercentage(self):
        if self.roundsWithFlop > 0:
            return self.flopWins / self.roundsWithFlop * 100
        else:
            return 0
    
    def turnWinPercentage(self):
        if self.roundsWithTurn > 0:
            return self.turnWins / self.roundsWithTurn * 100
        else:
            return 0
    
    def riverWinPercentage(self):
        if self.roundsWithRiver > 0:
            return self.riverWins / self.roundsWithRiver * 100
        else:
            return 0
    
    def cardsOnWinPercentage(self):
        if self.roundsWithCardsOn > 0:
            return self.cardsOnWins / self.roundsWithCardsOn * 100
        else:
            return 0
    
    def agresiveness(self):
        if self.decisions > 0:
            return (self.raiseFromCheck + self.reRaise) / self.decisions * 100
        else:
            return 0
    
    def flopPerRounds(self, rounds):
        return self.roundsWithFlop / rounds * 100 if rounds > 0 else 0
    
    def turnPerRounds(self, rounds):
        return self.roundsWithTurn / rounds * 100 if rounds > 0 else 0
    
    def riverPerRounds(self, rounds):
        return self.roundsWithRiver / rounds * 100 if rounds > 0 else 0
    
    def cardsOnPerRounds(self, rounds):
        return self.roundsWithCardsOn / rounds * 100 if rounds > 0 else 0
    
    # this function simulates player action(what he does when it comes his turn)
    # in console will be displayed his cards, what is on table and call value
    # 0 bet is used to fold for simplicity, after that we extract the money
    def response(self, toCall, onTable, stage):
        self.decisions += 1
        print('Your hand:')
        displayCards(self.hand)
        if len(onTable) == 0: 
            print('Nothing on table')
        else:
            print('On table:')
            displayCards(onTable)
        diff = toCall - self.roundCoins
        if diff == 0:
            print('Check situation')
        else:
            print('Bet 0 if you want to fold or ' + str(diff) + ' to call or more')
        print('You have ' + str(self.coins) + ' coins')
        x = input('Enter your sum: ')
        x = int(x)
        while (x > 0 and x < diff and x != self.coins) or x > self.coins:
            x = input('Wrong bet, please enter another sum: ')
            x = int(x)
        if x > diff:
            if diff == 0:
                self.raiseFromCheck += 1
            else:
                self.reRaise += 1
        self.roundCoins += x
        self.coins -= x
        return x
