# -*- coding: utf-8 -*-

import deck
from itertools import combinations


'''
This file contains all functions to evaluate a hand
The hand is represented as a list of pairs card number, card type
Holdem hands are evaluated to decide the winner only after river,
when a total of 7 cards are implied
The majority of check functions(who tell wheter the player has this
hand ranking or not) returns -1 if false
'''

# ace can be interpreted as 1 or 14(next card to king)
# in most situations it's interpreted as 14
def aceProblem(x):
    if x == 1:
        return 14
    else:
        return x

# this function returns the frequency of numbers as a dictionary
def getFreq(hand):
    freq = dict()
    for (no, tp) in hand:
        x = aceProblem(no)
        freq[x] = freq.get(x, 0) + 1
    return freq

# this function removes card type information
# we don't need it to evaluate a straight for example
def getCardsNo(hand):
    res = []
    for (no, tp) in hand:
        res.append(aceProblem(no))
    return res

# this function returns true if cards in a hand have the same color
def sameColor(hand):
    colorSet = set()
    for (no, tp) in hand:
        colorSet.add(tp)
    return len(colorSet) == 1

# this function returns true if cards in a hand form a straight
def inARow(hand):
    hand = sorted(hand)
    for i in range(1, 5):
        if hand[i] - hand[i - 1] != 1:
            return False
    return True

# royal flush = straight flush with ace as highest card
def checkRoyalFlush(hand):
    res = checkStrFlush(hand)
    if res == 14:
        return 1
    return -1

'''
We check every combination of 5 cards for flush and straight
If no combination checks the above conditions, maximum remains -1
'''
def checkStrFlush(hand):
    maximum = -1
    comb = combinations(hand, 5)
    for cmb in list(comb):
        if (checkFlush(cmb) != -1):
            rs = checkStraight(cmb)
            maximum = max(maximum, rs)
    return maximum

# checks if we have four of a kind(a card with frequency equal to 4)
def checkFour(hand):
    freq = getFreq(hand)
    for no in range(15):
        if no in freq and freq[no] == 4:
            return no
    return -1

'''
check for full house, res2 is used for cards which appear twice and res3
for three times. It returns the pair (a, b), where a appears three times
and b twice. Notice that we can have 2 cards who appear three times, that's
why i append a card in res3 and in res2, too.
'''
def checkFull(hand):
    freq = getFreq(hand)
    res2 = []
    res3 = []
    maximum = []
    for no in range(15):
        if no in freq and freq[no] > 1:
            if freq[no] == 3:
                res3.append(no)
                res2.append(no)
            elif freq[no] == 2:
                res2.append(no)
    res3 = sorted(res3, reverse = True)
    res2 = sorted(res2, reverse = True)
    for i in res3:
        for j in res2:
            if i != j:
                maximum.append(i)
                maximum.append(j)
                return maximum
    return -1

# check if a hand is a flush. If we find a combination with this proprierty,
# we return the highest card
def checkFlush(hand):
    maximum = -1
    comb = combinations(hand, 5)
    for cmb in list(comb):
        if (sameColor(cmb)):
            numbers = getCardsNo(hand)
            maximum = max(numbers)
    return maximum

# it returns the highest card in a straight combination from hand if it exists
# and -1 otherwise
def checkStraight(hand):
    numbers = getCardsNo(hand)
    for i in numbers:
        # ace can form the lowest straight or the highest straight,
        # so we append both 1 and 14
        if i == 14:
            numbers.append(1)
    comb = combinations(numbers, 5)
    maximum = -1
    for cmb in list(comb):
        if (inARow(cmb)):
            maximum = max(cmb)
    return maximum


# checks three of a kind. In case we have two numbers, we select highest card 
def checkThree(hand):
    freq = getFreq(hand)
    res = []
    for no in range(15):
        if (no in freq and freq[no] == 3):
            res.append(no)
    if len(res) == 2:
        res = sorted(res)
        return res[-1]
    elif len(res) == 1:
        return res[0]
    return -1

# it returns the pair of cards numbers which form the two pairs
def checkTwoPairs(hand):
    freq = getFreq(hand)
    res = []
    for no in range(15):
        if (no in freq and freq[no] == 2):
            res.append(no)
    if len(res) == 3:
        res = sorted(res)
        res = res[1 : ]
        return res
    elif len(res) == 2:
        res = sorted(res)
        return res
    return -1


def checkOnePair(hand):
    freq = getFreq(hand)
    maximum = -1
    for no in range(15):
        if (no in freq and freq[no] == 2 and maximum < no):
            maximum = no
    return maximum

# it returns the highest card in a hand
def highCard(hand):
    maxCard = 1
    for (no, tp) in hand:
        maxCard = max(maxCard, aceProblem(no))
    return maxCard

# orderDict contains the hand ranking order
# and handsDict connects ranking to coresponding check function

handsDict = {"royalFlush" : checkRoyalFlush, "straightFlush" : checkStrFlush,
             "four" : checkFour, "fullHouse" : checkFull, "flush" : checkFlush,
             "straight" : checkStraight, "three" : checkThree,
             "twoP" : checkTwoPairs, "oneP" : checkOnePair, "high" : highCard}


orderDict = {"royalFlush" : 0, "straightFlush" : 1, "four" : 2,
             "fullHouse" : 3, "flush" : 4, "straight" : 5, "three" : 6,
             "twoP" : 7, "oneP" : 8, "high" : 9}


# this function applies every check function from the best ranked hand to
# weakest. HandOrder is the value from orderDict of the best hand found
# and best card is the max card number from that combination
def handResult(hand):
    bestCard = -1
    handOrder = -1
    for handRes in handsDict.keys():
        func = handsDict[handRes]
        mx = func(hand)
        if mx != -1:
            bestCard = mx
            handOrder = orderDict[handRes]
            break
    return handOrder, bestCard

def compareInts(a, b):
    if a > b:
        return 1
    if a < b:
        return -1
    return 0

# when two players have the same hand ranking, for some rankings the highest
# card not involved in that pair, two pair,etc. makes the difference
def highestCard(hand, cardsExcluded):
    res = []
    for card in hand:
        if card not in cardsExcluded:
            res.append(card)
    return max(res)

# it compares two hands and tells who wins(1-hand1, 0-draw, -1-hand2)
# there are a lost of cases when the players have the same hand ranking
def compareTwoHands(hand1, hand2):
    handOrd1, best1 = handResult(hand1)
    handOrd2, best2 = handResult(hand2)
    if handOrd1 < handOrd2:
        return 1
    if handOrd1 > handOrd2:
        return -1
    if handOrd1 in [1, 4, 5]:
        return compareInts(best1, best2)
    if handOrd1 == 3:
        res = compareInts(best1[0], best2[0])
        if res != 0:
            return res
        else:
            return compareInts(best1[1], best2[1])
    l1 = best1
    l2 = best2
    if handOrd1 != 7:
        l1 = []
        l2 = []
        l1.append(best1)
        l2.append(best2)
    if handOrd1 in [2, 6, 8, 9]:
        res = compareInts(best1, best2)
        if res != 0:
            return res
    if handOrd1 == 7:
        res = compareInts(best1[1], best2[1])
        if res != 0:
            return res
        else:
            res = compareInts(best1[0], best2[0])
            if res != 0:
                return res
    remains1 = highestCard(hand1, l1)
    remains2 = highestCard(hand2, l2)
    if remains1 > remains2:
        return 1
    elif remains1 < remains2:
        return -1
    return 0
        

# this function receives a list of hands and returns a list of winners
# it use a dictionary for every player with the role of a win counter
# and evaluates every 1vs1 duel. The player/players with most wins take the pot
def compareMoreHands(hands):
    wins = {}
    maximumWins = -1
    for i in range(len(hands)):
        wins[i] = 0
    for i in range(len(hands)):
        for j in range(i + 1, len(hands)):
            rs = compareTwoHands(hands[i], hands[j])
            if rs == 1:
                wins[i] = wins.get(i, 0) + 1
            elif rs == -1:
                wins[j] = wins.get(j, 0) + 1
    for i in wins.keys():
        maximumWins = max(maximumWins, wins[i])
    winners = []
    for i in range(len(hands)):
        if wins[i] == maximumWins:
            winners.append(i)
    return winners
