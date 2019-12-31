import os
import json
from tabulate import tabulate

if os.name != "posix":
    clear = lambda: os.system('cls') #on Windows System
else:
    clear = lambda: os.system('clear')  # on Windows System

players = list()
matches = list()

class Player:
    def __init__(self, name):
        self.name = name
        self.colors = list()
        self.bans = dict()
        self.score = 0

    def addColor(self, color):
        self.colors.append(color)

    def printDecks(self):
        i = 1
        for color in self.colors:
            print(str(i) + " - " + color)
            i = i+1


    def print(self):
        print(self.name + " - score: " + str(self.score))
        self.printDecks()
        print("--bans:")
        for ban in self.bans:
            print("against " + ban.name + ":")
            for deck in self.bans[ban]:
                print("  " + deck)

    def asJson(self):
        return {"name": self.name,
                "decks": [deck for deck in self.colors],
                "bans": {ban.name: self.bans[ban] for ban in self.bans}}

class Match:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.winsP1 = 0
        self.winsP2 = 0

    def printLine(self):
        if self.isOpen():
            print("   -:- " + self.p1.name + " - " + self.p2.name)
        else:
            print("   " + str(self.winsP1) + ":" + str(self.winsP2) + " " + self.p1.name + " - " + self.p2.name)

    def printMatch(self):
        p1Decks = list()
        p1Bans = list()
        p2Decks = list()
        p2Bans = list()
        for deck in self.p1.colors:
            if deck not in self.p2.bans[self.p1]:
                p1Decks.append(deck)
            else:
                p1Bans.append(deck)
        for deck in self.p2.colors:
            if deck not in self.p1.bans[self.p2]:
                p2Decks.append(deck)
            else:
                p2Bans.append(deck)
        print(self.p1.name + " vs. " + self.p2.name)
        print()
        print(tabulate([[p1Decks[i], p2Decks[i]] for i in range(len(p1Decks))],
                       headers=[self.p1.name, self.p2.name],
                       tablefmt='orgtbl'))
        print()
        print("Banned:")
        print(tabulate([[p1Bans[i], p2Bans[i]] for i in range(len(p1Bans))],
                       headers=[self.p1.name, self.p2.name],
                       tablefmt='orgtbl'))

        if not self.isOpen():
            print("Result:")
            print("   " + self.p1.name + ": " + str(self.winsP1))
            print("   " + self.p2.name + ": " + str(self.winsP2))

    def isOpen(self):
        return self.winsP1 == 0 and self.winsP2 == 0


def saveState():
    playerList = {"players": [player.asJson() for player in players]}

    jsonDict = json.dumps(playerList)
    f = open("bak.json", "w")
    f.write(jsonDict)
    f.close()

def printHeader():
    clear()
    print("#################################################")
    print("# fire-server MTG tournament helper             #")
    print("#################################################")
    print()

def createPlayer():
    printHeader()
    playerName = input("Enter Player Name: ")
    print("Welcome player " + playerName + "!")
    player = Player(playerName)
    print("Which decks are you gonna play: ")
    print("(R=red, G=green, U=blue, W=white, B=black)")
    i = 0
    while i < 5:
        i = i+1
        deckColor = input("  " + str(i) + ":")
        player.colors.append(deckColor)
    printHeader()
    print("Please review your entries, " + playerName)
    player.printDecks()
    nio = True
    while nio:
        print("Do you want to add the player to the list? Y/n ")
        sel = input()
        if sel == "y" or sel == "":
            nio = False
            players.append(player)
            printHeader()
            print("Add another player? Y/n ")
            selAnother = input()
            if selAnother == "y" or selAnother == "":
                createPlayer()
            else:
                banPhase()
        elif sel == "n":
            nio = False
            createPlayer()

def banPlayer(idx):
    printHeader()
    print(players[idx].name + " select your bans:")
    input("Begin")
    for player in players:
        if player is players[idx]:
            continue
        nio = True
        while nio:
            printHeader()
            print("Bans of player " + players[idx].name)
            print("Bans against \"" + player.name + "\":")
            player.printDecks()
            bans = list()
            while len(bans) < 2:
                banId = 0
                while banId <= 0 or banId > 5:
                    banId = int(input("Index of Deck to ban (1-5): "))
                    if banId <= 0 or banId > 5:
                        print("Invalid number!")
                bans.append(player.colors[banId - 1])
            print()
            print("you selected ")
            for deck in bans:
                print("  " + deck)
            print("as your bans against " + player.name)
            notApproved = True
            while notApproved:
                sel = input("Do you want to continue? Y/n ")
                if sel == "y" or sel == "":
                    nio = False
                    notApproved = False
                    players[idx].bans[player] = bans
                elif sel == "n":
                    notApproved = False

def banPhase():
    printHeader()
    i = 0
    saveState()
    while i < len(players):
        banPlayer(i)
        i = i+1
    saveState()
    prepareGame()

def prepareGame():
    printHeader()
    print("setting up...")
    if len(players) % 2 == 1:
        players.append(Player("__Break__"))
        print("odd player count detected, adding break player")

    for p1 in range(len(players)):
        for p2 in range(p1 + 1, len(players)):
            matches.append(Match(players[p1], players[p2]))

    ingameMenu()


def genMatches(source):
    result = []
    for p1 in range(len(source)):
        for p2 in range(p1 + 1, len(source)):
            result.append([source[p1], source[p2]])
    return result

def newGame():
    printHeader()
    print("-- Player Setup --")
    players.clear()
    matches.clear()
    createPlayer()

def load():
    players.clear()
    matches.clear()
    loadedPlayers = dict()
    with open('bak.json') as json_file:
        data = json.load(json_file)
        for player in data["players"]:
            loadedPlayers[player["name"]] = Player(player["name"])
            players.append(loadedPlayers[player["name"]])
            for deck in player["decks"]:
                players[len(players) - 1].colors.append(deck)
        for player in data["players"]:
            print(" update player " + player["name"] + "with bans: ", player["bans"])
            for banplayer in player["bans"].keys():
                otherPlayerName = banplayer
                #otherPlayerName = list(banplayer.keys())[0]
                print("  player " + player["name"] + " add ban for " + otherPlayerName)
                loadedPlayers[player["name"]].bans[loadedPlayers[otherPlayerName]] = list()
                for ban in player["bans"][otherPlayerName]:
                    print("    in ban " + ban)
                    loadedPlayers[player["name"]].bans[loadedPlayers[otherPlayerName]].append(ban)

    print("loaded")
    for player in players:
        print(player)
        print("bans:")
        for ban in player.bans:
            print(ban)

    input("..")
    prepareGame()
#    playerList = {"players": [player.asJson() for player in players]}

def selectMatch(showAll = False):
    matchSet = dict()
    i = 1
    for match in matches:
        if showAll or match.isOpen():
            matchSet[i] = match
            print("  (" + str(i) + ") " + match.p1.name + " - " + match.p2.name)
            i = i+1
    sel = 0
    while sel not in matchSet:
        sel = int(input("Select match to enter results. (0) for cancel "))
        if sel == 0:
            ingameMenu()

    return matchSet[sel]

def enterResults():
    printHeader()
    match = selectMatch()
    nio = True
    p1Wins = int(input("Wins of " + match.p1.name + ": "))
    #p2Wins = input("Wins of " + match.p2.name + ": ")
    p2Wins = 3-p1Wins
    approved = input(str(p1Wins) + " : " + str(p2Wins) +
                     " will be entered as match result for " + match.p1.name +
                     " vs " + match.p2.name + " and match will be closed. Proceed? y/n ")
    if approved == "y":
        match.winsP1 = p1Wins
        match.winsP2 = p2Wins
    ingameMenu()


def showMatchDetails():
    printHeader()
    match = selectMatch()
    match.printMatch()
    print()
    input(". . .")
    ingameMenu()

def sortFun(val):
    return val.score

def showResults():
    for player in players:
        player.score = 0
    for match in matches:
        match.p1.score = match.p1.score + match.winsP1
        match.p2.score = match.p2.score + match.winsP2
    printHeader()
    players.sort(key=sortFun, reverse=True)
    print("Results:")
    i = 0
    lastScore = players[0].score + 1
    for player in players:
        if lastScore > player.score:
            i = i+1
            lastScore = player.score
        print("  " + str(i) + ". - " + player.name + "(" + str(player.score) + ")")
    print()
    input(". . .")
    ingameMenu()


def ingameMenu():
    printHeader()
    print("- Standings ------------")
    for match in matches:
        match.printLine()
    print("------------------------")
    print("Actions:")
    print("  (1) show results")
    print("  (2) show matches")
    print("  (3) show match details")
    print("  (4) enter results")
    sel = input()
    if sel == "1":
        showResults()
    elif sel == "2":
        ingameMenu()
    elif sel == "3":
        showMatchDetails()
    elif sel == "4":
        enterResults()
    else:
        ingameMenu()

def mainMenu():
    printHeader()
    print("  (1) New Game")
    print("  (2) Load")
    menuSel = input()
    if menuSel == "1":
        newGame()
    elif menuSel == "2":
        load()


mainMenu()
#playerSet1 = [i for i in range(4)]
#random.shuffle(playerSet1)
