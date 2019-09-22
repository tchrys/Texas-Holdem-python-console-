# -*- coding: utf-8 -*-

import deck
from player import Player
import player as plr
import hands
import time

# next player in order of betting
def nextPlayer(button, length):
    return (button + 1) % length

# this returns a list of players order according to start player
# we treat the table as a circular array
def getPlayersOrder(startPlayer, length):
    res = []
    i = startPlayer
    while i < length:
        res.append(i)
        i += 1
    i = 0
    while i < startPlayer:
        res.append(i)
        i += 1
    return res


class Round:
    
    def __init__(self, blind, players, button, statsList):
        self.bigBlind = blind
        self.smallBlind = blind // 2
        self.players = []
        for i in players:
            pl = Player()
            pl.getProps(i)
            self.players.append(pl)
        self.button = button
        self.pot = 0
        self.stats = statsList
        # toCall represents how much you must best bet in that round to stay
        # in game from beginning(not just at flop, turn etc)
        self.toCall = blind
        # raiser = last player who raised
        self.raiser = -1    
        self.length = len(self.players)
        self.onTable = []
        # smallPlayer(the one with small blind) starts every phase excepting
        # the one before flop
        # startPlayer starts the first phase
        afterBlinds = nextPlayer(button, self.length)
        afterBlinds = nextPlayer(afterBlinds, self.length)
        self.startPlayer = nextPlayer(afterBlinds, self.length)
        self.smallPlayer = nextPlayer(button, self.length)
        # special case for 2 players
        if self.length == 2:
            self.startPlayer = self.smallPlayer
        self.toCall = blind
        # key = indeces of all-in players, value = how much they earn if they
        # have the best hand
        self.allInPlayers = dict()
        
    # we must extract blinds
    def resolveButton(self):
        pLen = len(self.players)
        for i in range(pLen):
            print(self.players[i].coins)
        res = self.players[self.smallPlayer].extractBlind(self.smallBlind)
        self.pot += res
        if res < self.smallBlind:
            self.allInPlayers[self.smallPlayer] = res
        self.players[self.smallPlayer].roundCoins = res
        bigButton = self.smallPlayer + 1
        if bigButton == pLen:
            bigButton = 0
        res = self.players[bigButton].extractBlind(self.bigBlind)
        self.pot += res
        if res < self.bigBlind:
            self.allInPlayers[bigButton] = res
        self.players[bigButton].roundCoins = res
        
    def howManyInvestedAtLeast(self, coins):
        res = 0
        for pl in self.players:
            if pl.roundCoins >= coins:
                res += 1
        return res
        
    # if a player went all-in, we must compute his pot share
    def resolveAllInPlayers(self):
        for k in range(self.length):
            if self.players[k].allIn() and k not in self.allInPlayers:
                self.allInPlayers[k] = self.players[k].roundCoins * \
                        self.howManyInvestedAtLeast(self.players[k].roundCoins)
                for j in range(self.length):
                    if j != k and self.players[j].roundCoins < self.players[k].roundCoins:
                        self.allInPlayers[k] += self.players[j].roundCoins
        
    # in each round,at start, we shuffle the deck and share cards to players
    def startRound(self):
        dck = deck.Deck()
        self.deck = dck
        for player in self.players:
            player.receiveCard(self.deck.getTopCard())
            player.receiveCard(self.deck.getTopCard())
            plr.displayCards(player.hand)
        self.resolveButton()
        
    # at end we reset some stats and remove losers from table
    def finishRound(self):
        losers = []
        for i in range(self.length):
            if self.players[i].isBankrupt():
                losers.append(i)
        for index in sorted(losers, reverse=True):
            del self.players[index]
        for pl in self.players:
            pl.hand = []
            pl.inGame = True
        return self.players
    
    # round stages: betting - flop - betting - turn - betting - river - betting
    # if just one player remains in game after a stage, there is no reason
    # to continue
    def roundProcess(self):
        self.startRound()
        print('Betting process starts')
        ok = self.bettingProcess(self.startPlayer, 'preflop')
        print('Before flop, pot is ' + str(self.pot))
        if ok:
            self.putFlop()
            plInGame = self.getPlayersInGame()
            for j in plInGame:
                self.players[j].roundsWithFlop += 1
            ok = self.bettingProcess(self.smallPlayer, 'flop')
            print('Flop finished, pot is now ' + str(self.pot))
            if self.allInSituation() and ok:
                time.sleep(1)
            plr.displayCards(self.onTable)
            if ok:
                self.putTurn()
                plInGame = self.getPlayersInGame()
                for j in plInGame:
                    self.players[j].roundsWithTurn += 1
                ok = self.bettingProcess(self.smallPlayer, 'turn')
                print('Turn finished, pot is now ' + str(self.pot))
                plr.displayCards(self.onTable)
                if ok:
                    self.putRiver()
                    plInGame = self.getPlayersInGame()
                    for j in plInGame:
                        self.players[j].roundsWithRiver += 1
                    ok = self.bettingProcess(self.smallPlayer, 'river')
                    print('River finished, pot is now ' + str(self.pot))
                    plr.displayCards(self.onTable)
                    if ok:
                        plInGame = self.getPlayersInGame()
                        for j in plInGame:
                            self.players[j].roundsWithCardsOn += 1
                        self.giveToBest()
        return self.finishRound()
    
    def allInSituation(self):
        return len(self.getPlayersInGame()) - self.playersNoAllIn() < 2
    
    def putFlop(self):
        self.deck.popCard()
        self.onTable.append(self.deck.getTopCard())
        self.onTable.append(self.deck.getTopCard())
        self.onTable.append(self.deck.getTopCard())
    
    def putTurn(self):
        self.deck.popCard()
        self.onTable.append(self.deck.getTopCard())
        
    def putRiver(self):
        self.deck.popCard()
        self.onTable.append(self.deck.getTopCard())
    
    # it returns false if there is some player in game who haven't made his
    # decision yet, otherwise it returns true
    def betsFinished(self):
        for player in self.players:
            if player.allIn():
                continue
            if player.inGame == True and player.roundCoins != self.toCall:
                return False
        return True
    
    # returns the number of players who went all in
    def playersNoAllIn(self):
        no = 0
        for i in range(self.length):
            if self.players[i].allIn():
                no += 1
        return no
    
    # it returns a list with indeces of players in game
    def getPlayersInGame(self):
        res = []
        for i in range(self.length):
            if self.players[i].inGame == True:
                res.append(i)
        return res
    
    def noAllInWinner(self, winners, finalists):
        for i in winners:
            winnerPlayer = finalists[i]
            if winnerPlayer in self.allInPlayers:
                return False
        return True
    
    def findFirstAllInWinner(self, winners, finalists):
        for i in winners:
            winnerPlayer = finalists[i]
            if winnerPlayer in self.allInPlayers:
                return winnerPlayer
        return -1
    
    def getBets(self, finalists):
        res = []
        for i in finalists:
            res.append(self.players[i].roundCoins)
        return res
    
    
    # if a player went all in and bet more money than others we subtract
    # that surplus of coins from the pot and add them to player's coins
    # example : 5, 7, 8 -> player with 8 bet gets 1 coin back
    def solveAllInBets(self, finalists):
        bets = self.getBets(finalists)
        st = set(bets)
        if len(st) == 1:
            return
        maxBet = 0
        nextBet = 0
        for bt in bets:
            if maxBet < bt:
                maxBet = bt
        for bt in bets:
            if bt != maxBet and nextBet < bt:
                nextBet = bt
        diff = maxBet - nextBet
        for i in finalists:
            if self.players[i].roundCoins == maxBet:
                self.players[i].coins += diff
                self.pot -= diff
                
        
    
    # if we get to last stage we must get player's cards and call
    # compareMoreHands from hands to get the winners and share the pot to them
    # notice i took care of players who went all-in(they do not get
    # the same amount normally). If there are more winners and one of them
    # is an all-in player, he gets his share first, and the rest of the pot is
    # shared to the rest of finalists
    def giveToBest(self):
        print('Pot is now ' + str(self.pot))
        if self.pot == 0:
            return
        finalists = self.getPlayersInGame()
        if len(finalists) == 1:
            self.players[finalists[0]].coins += self.pot
            return
        self.solveAllInBets(finalists)
        plHands = []
        print('Finalists are ' + str(finalists))
        for j in finalists:
            hand = []
            for card in self.players[j].hand:
                hand.append(card)
            for card in self.onTable:
                hand.append(card)
            handToDeck = deck.getHand(hand)
            plHands.append(handToDeck)
        winners = hands.compareMoreHands(plHands)
        allInWinner = self.findFirstAllInWinner(winners, finalists)
        if allInWinner == -1:
            money = self.pot // len(winners)   
            for i in winners:
                winnerPlayer = finalists[i]
                print('Plr with number ' + str(winnerPlayer) + ' wins ' + str(money))
                self.players[winnerPlayer].cardsOnWins += 1
                self.players[winnerPlayer].coins += money
                moneyInvested = self.players[winnerPlayer].roundCoins
                self.players[winnerPlayer].winnings += money - moneyInvested
        else:
            # the winner is the richest so he takes all
            moneyInvested = self.players[allInWinner].roundCoins
            if self.howManyInvestedAtLeast(moneyInvested) == 1:
                self.players[allInWinner].cardsOnWins += 1
                self.players[allInWinner].coins += self.pot
                self.players[allInWinner].winnings += self.pot - moneyInvested
                print('Player ' + str(allInWinner) + ' wins ' + str(self.pot))
                return
            else:
                coinsWon = self.allInPlayers[allInWinner]
                self.players[allInWinner].cardsOnWins += 1
                self.players[allInWinner].coins += coinsWon
                self.players[allInWinner].winnings += coinsWon - moneyInvested
                self.pot -= coinsWon
                self.players[allInWinner].inGame = False
                print('Player ' + str(allInWinner) + ' wins ' + str(coinsWon))
                self.giveToBest()
    
    # it returns True if more than one player remains in game
    def bettingProcess(self, startPlayer, stage):
        if self.allInSituation():
            return True
        while True:
            # get betting order
            order = getPlayersOrder(startPlayer ,self.length)
            for j in order:
                # we skip that player if he is not in game, also if he raised
                if self.players[j].inGame == True and self.raiser != j:
                    if len(self.getPlayersInGame()) == 1:
                        # only one in game so we skip him,same for all-in
                        break
                    if self.players[j].allIn():
                        break
                    diff = self.toCall - self.players[j].roundCoins
                    if diff == 0 and self.players[j].called:
                        break
                    print('player ' + str(j) + ' response, has to call ' + str(diff))
                    playerBet = self.players[j].response(self.toCall, self.onTable, stage)
                    print('Round coins for ' + str(j) + ' ' + str(self.players[j].roundCoins))
                    if diff > playerBet and playerBet != 0:
                        # all in
                        print('He went all in')
                        self.pot += playerBet
                    elif playerBet == 0 and diff == 0:
                        print('He checks')
                    elif playerBet == 0 and diff != 0:
                        # fold
                        print('He folds')
                        self.players[j].inGame = False
                    elif diff == playerBet:
                        # call
                        print('He calls')
                        self.pot += playerBet
                        self.players[j].called = True
                    elif diff < playerBet:
                        # raise
                        print('Raised ' + str(playerBet))
                        self.raiser = j
                        self.pot += playerBet
                        self.toCall += playerBet - diff
            if self.betsFinished() == True:
                break
        self.raiser = -1   # nobody is the raiser now
        # if one player raised and everyone else folded, that player
        # takes the pot and this round is actually finished
        playersInGame = self.getPlayersInGame()
        if len(playersInGame) == 1:
            self.players[playersInGame[0]].coins += self.pot
            moneyInvested = self.players[playersInGame[0]].roundCoins
            self.players[playersInGame[0]].winnings += self.pot - moneyInvested
            if stage == 'preflop':
                self.players[playersInGame[0]].preFlopWins += 1
            elif stage == 'flop':
                self.players[playersInGame[0]].flopWins += 1
            elif stage == 'turn':
                self.players[playersInGame[0]].turnWins += 1
            elif stage == 'river':
                self.players[playersInGame[0]].riverWins += 1
            return False
        else:
            self.resolveAllInPlayers()
            for pl in self.players:
                pl.called = False
            return True
