# -*- coding: utf-8 -*-

import random

'''
C - clubs
D - diamonds
H - hearts
S - spades
'''
typeCardDict = {'C' : 0, 'D' : 1, 'H' : 2, 'S' : 3}

'''
Cards are numbered in this order: clubs, diamonds, hearts, spades, from ace(0),
two(1), three(2), ..., to kings(13)
'''

# there are 52 cards in a texas holdem deck
def shuffleDeckList():
    lst = []
    for i in range(52):
        lst.append(i)
    random.shuffle(lst)
    return lst

# deck class contains a list which represents the deck
# the top card is obviously at zero index

class Deck:
    def __init__(self):
        self.deck = shuffleDeckList()
    
    def getDeck(self):
        return self.deck
    
    def getCard(self, id):
        return self.deck[id]
    
    def getTopCard(self):
        top = self.deck[0]
        del self.deck[0]
        return top
    
    def popCard(self):
        del self.deck[0]
    

'''
Given an id, the function returns the card as a string
Example : ace of clubs -> 1C
Notice that we must increment cards number(ace is 0, two is 1, etc)
'''

def getCardString(id):
        quot = id // 13
        rem = id % 13
        cardType = ''
        if quot == 0:
            cardType = 'C'
        elif quot == 1:
            cardType = 'D'
        elif quot == 2:
            cardType = 'H'
        else:
            cardType = 'S'
        res = str(1 + rem)
        res += cardType
        return res
    
# it returns card's number
    
def getCardNr(id):
    res = getCardString(id)
    return int(res[ : -1])

# same for type

def getCardType(id):
    res = getCardString(id)
    return res[-1]
    
# function to visualize a list of cards

def getStringHand(lst):
    res = []
    for card in lst:
        res.append(getCardString(card))
    return res

# lst is a list of cards(as numbers)
# it returns the list of pairs(number, type)

def getHand(lst):
    res = []
    for card in lst:
        t = (getCardNr(card), (typeCardDict[getCardType(card)]))
        res.append(t)
    res = sorted(res)
    return res
        