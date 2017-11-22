from random import randint

class Zone:
    def __init__(self, **kwargs):
        self.nodeID = None
        self.nodeName = None
        self.sphere = None
        self.production = None
        self.petrol = None
        self.interest = None
        self.capital = None

class Player:
    def __init__(self):
        self.army = {}
        self.hand = []
        self.capital = None

    def ListArmy(self):
        print("You have units in:\n")
        for x in self.army.keys():
            print("{}:{}\n".format(x,self.army[x]))
 

class GameBoard:
    def __init__(self, **kwargs):
        self.round = None
        self.zones_data = []
        self.edges_pairs = []
        self.availableCapitals = []
        self.turn_deck = None
        self.players = {}

    def DataBoardParse(self):
        f = open("SpheresDataBoard.csv","r")
        for x in range(0, 100):
            line = f.readline()
            data = line.split(";")
            newzone = Zone()
            newzone.nodeID = int(data[0])
            newzone.nodeName = data[1]
            newzone.sphere = int(data[2])
            newzone.production = int(data[3])
            newzone.petrol = bool(int(data[4]))
            newzone.interest = bool(int(data[5]))
            newzone.capital = bool(int(data[6]))
            self.zones_data.append(newzone)
        f.close()

    def EdgeParse(self):
        f = open("IncidenceT2.txt","r")
        while True:
            line = f.readline()
            if len(line) < 3:
                break
            newedge_A = None
            for y in range(0, 100):
                if line[y] == '1':
                    if newedge_A == None:
                        newedge_A = y
                    else:
                        newedge = (newedge_A, y)
                        break
            self.edges_pairs.append(newedge)
        f.close()

    def ListZoneConnections(self,id):
        print("Las conexiones del nodo {}, de nombre '{}' son:\\ ".format(id, self.zones_data[id].nodeName))
        i = 0
        while i < len(self.edges_pairs):
            if self.edges_pairs[i][0] == id:
                print(self.zones_data[self.edges_pairs[i][1]].nodeName)
                i = i + 1
                continue
            if self.edges_pairs[i][1] == id:
                print(self.zones_data[self.edges_pairs[i][0]].nodeName)
            i = i + 1

    def ZoneConnections(self,id):
        result = []
        i = 0
        while i < len(self.edges_pairs):
            if self.edges_pairs[i][0] == id:
                result.append(self.zones_data[self.edges_pairs[i][1]].nodeName)
                i = i + 1
                continue
            if self.edges_pairs[i][1] == id:
                result.append(self.zones_data[self.edges_pairs[i][0]].nodeName)
            i = i + 1
        return result

    def FindZoneByName(self,name):
        i = 0
        while i < len(self.zones_data):
            if self.zones_data[i].nodeName == name:
                return i
            i = i + 1


    def CreatePlayers(self,n):
        for x in range(n):
            #Allow name selection
            names = ['atlas','bizencio','chipre','dedalo','eleonora','firulais','gabo']
            selected_name = names[x]
            self.players[selected_name] = Player()
            self.OfferCapitals(selected_name)

    def PopulateAvailableCapitals(self):
        for zone in self.zones_data:
            if zone.capital:
                self.availableCapitals.append((zone.nodeName))

    def OfferCapitals(self,player):
        if len(self.availableCapitals) <= 4:
            print("Not enough miner..capitals")
            return 1
        random_number = randint(0, len(self.availableCapitals) - 1)
        optionA = self.availableCapitals[random_number]
        del self.availableCapitals[random_number]
        random_number = randint(0, len(self.availableCapitals) - 1)
        optionB = self.availableCapitals[random_number]
        del self.availableCapitals[random_number]
        print("You can choose between {} and {}\n".format(optionA,optionB))
        #Allow some selection
        selected = optionA
        print("Good, your selected capital is {}. 3 units will be added here\n".format(selected))
        self.players[player].capital = selected
        self.players[player].army[self.players[player].capital] = 3

    def addToPlayerArmy(self,player,place,n):
        if player in self.players:
            if place in self.players[player].army:
                self.players[player].army[place] = self.players[player].army[place] + n
            else:
                self.players[player].army[place] = n
            return 0
        else:
            print("Player doesn't exist")
            return 1

    def movePlayerArmy(self,player,placeA,placeB,n):
        if player in self.players:
            if placeA in self.players[player].army:
                if(self.players[player].army[placeA] - n) < 1:
                    print("You do not have enough units to make that action")
                    return 1
                for pkey in list(self.players.keys()):
                    if placeB in self.players[pkey].army:
                        if pkey == player:
                           print("It's a valid move. Go on.")
                           self.players[player].army[placeA] = self.players[player].army[placeA] - n
                           self.players[player].army[placeB] = self.players[player].army[placeB] + n
                        else:
                           print("It's an attack!")
                           #Combat()!!!!!
                        return 0
                #It is an empty zone then
                print("Conquest!!!!")
                self.players[player].army[placeA] = self.players[player].army[placeA] - n
                self.players[player].army[placeB] = n
                return 0
            else:
                print("Invalid move. You do not control that territory")
                return 1
        else:
            print("What the fuck? This palyer doesn't even exist")
            return 1

    def MoveArmyIfTerrainAllows(self, player, placeA, placeB, n):
        print("Trying to move from {} to {}\n".format(placeA, placeB))
        all_d1_zones = self.ZoneConnections(self.FindZoneByName(placeA))
        if placeB in all_d1_zones:
            return self.movePlayerArmy(player, placeA, placeB, n)
        if self.zones_data[self.FindZoneByName(placeB)].sphere == 0:
            all_d2_zones = []
            water_d1_zones = []
            for zone in all_d1_zones:
                if self.zones_data[self.FindZoneByName(zone)].sphere == 0:
                    water_d1_zones.append(zone)
            for some_d1_zone in water_d1_zones:
                some_d2_zones = self.ZoneConnections(some_d1_zone)
                for d2zone in some_d2_zones:
                    if not d2zone in all_d2_zones:
                        all_d2_zones.append(d2zone)
            if placeB in all_d2_zones:
                return self.movePlayerArmy(player, placeA, placeB, n)
        else:
            print("Invalid movement")
            return 1



            
