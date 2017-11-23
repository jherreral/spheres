import copy
import math
import random
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
        self.name = None
        self.army = {}
        self.hand = []
        self.capital = None

    def ListArmy(self):
        print("You have units in:\n")
        for x in self.army.keys():
            print("{}:{}\n".format(x,self.army[x]))
 

class GameBoard:
    def __init__(self, **kwargs):
        self.round = 0
        self.zones_data = []
        self.edges_pairs = []
        self.availableCapitals = []
        self.movilization_order = []
        self.turn_deck = []
        self.players = []
        self.zones_per_sphere = [0]*18

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

    def CalculateZonesPerSphere(self):
        for zone in self.zones_data:
            if zone.sphere == 0:
                continue
            self.zones_per_sphere[zone.sphere - 1] = self.zones_per_sphere[zone.sphere - 1] + 1
        return 0

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

    def FindPlayerByName(self,player_name):
        i = 0
        while i < len(self.players):
            if self.players[i].name == player_name:
                return i
            i = i + 1

    def CreatePlayers(self,n):
        for player_id in range(n):
            #->Allow name selection
            names = ['Harturo','Bernardo','Carolina','Daniel','Eleonora','Francis','Gabo']
            selected_name = names[player_id]
            self.players.append(Player())
            self.players[player_id].name = selected_name
            self.OfferCapitals(player_id)

    def PopulateAvailableCapitals(self):
        for zone in self.zones_data:
            if zone.capital:
                self.availableCapitals.append((zone.nodeName))

    def OfferCapitals(self,player_id):
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
        self.players[player_id].capital = selected
        self.players[player_id].army[self.players[player_id].capital] = 3

    def addToPlayerArmy(self,player_id,place,n):
        if self.players[player_id].name != 'Dead':
            if place in self.players[player_id].army:
                self.players[player_id].army[place] = self.players[player_id].army[place] + n
            else:
                self.players[player_id].army[place] = n
            return 0
        else:
            print("Player is dead")
            return 1

    def movePlayerArmy(self,player_id,placeA,placeB,n):
        if self.players[player_id].name != 'Dead':
            if placeA in self.players[player_id].army:
                if(self.players[player_id].army[placeA] - n) < 1:
                    print("You do not have enough units to make that action")
                    return 1
                for i in range(len(self.players)):
                    if placeB in self.players[i].army:
                        if i == player_id:
                           print("It's a valid move. Go on.")
                           self.players[player_id].army[placeA] = self.players[player_id].army[placeA] - n
                           self.players[player_id].army[placeB] = self.players[player_id].army[placeB] + n
                        else:
                           print("It's an attack!")
                           #Combat()!!!!!
                        return 0
                #It is an empty zone then
                print("Conquest!!!!")
                self.players[player_id].army[placeA] = self.players[player_id].army[placeA] - n
                self.players[player_id].army[placeB] = n
                return 0
            else:
                print("Invalid move. You do not control that territory")
                return 1
        else:
            print("Those troops lost the will to fight")
            return 1

    def MoveArmyIfTerrainAllows(self, player_id, placeA, placeB, n):
        print("Trying to move from {} to {}\n".format(placeA, placeB))
        all_d1_zones = self.ZoneConnections(self.FindZoneByName(placeA))
        if placeB in all_d1_zones:
            return self.movePlayerArmy(player_id, placeA, placeB, n)
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
                return self.movePlayerArmy(player_id, placeA, placeB, n)
        else:
            print("Invalid movement")
            return 1

    def ArrangeTurnDeck(self):
        self.turn_deck.clear()
        for i in range(len(self.players)):
            self.turn_deck.append(i)
            self.turn_deck.append(i)
            if self.round > 1:
                for zones in self.players[i].army:
                    if self.zones_data[self.FindZoneByName(zones)].petrol:
                        self.turn_deck.append(p)
        random.shuffle(self.turn_deck)
        return 0

    def CalculateProdSpheCaps(self):
        nPlayers = len(self.players)
        total_productions = [0]*nPlayers
        (nSphes,nCaps) = self.CheckSpheres()
        for i in range(nPlayers):
            for zone in self.players[i].army:
                total_productions[i] = total_productions[i] + self.zones_data[self.FindZoneByName(zone)].production
        return (total_productions, nSphes, nCaps)

    def ArrangeMovilizationDeck(self):
        nPlayers = len(self.players)
        players_to_sort = []
        (total_productions, nSphes, nCaps) = self.CalculateProdSpheCaps()
        for i in range(nPlayers):
            players_to_sort.append((i,) + (total_productions[i],) + (nSphes[i],) + (nCaps[i],))

        sorted_by_cap = sorted(players_to_sort, key = lambda x:x[3])
        sorted_by_sph = sorted(sorted_by_cap, key = lambda x:x[2])
        sorted_by_pro = sorted(sorted_by_sph, key = lambda x:x[1], reverse = True)
        self.movilization_order = [x[0] for x in sorted_by_pro]
        print("Movilization order ready:\n")
        for i in range(nPlayers):
            print("{}:Player {} with {} production\n".format(i + 1, self.players[self.movilization_order[i]].name, sorted_by_pro[i][1]))
        return 0

    def CheckSpheres(self):
        nPlayers = len(self.players)
        nSpheres = [0]*nPlayers
        nCapitals = [0]*nPlayers
        for i in range(nPlayers):
            sphere_counter = copy.copy(self.zones_per_sphere)
            for zone in self.players[i].army:
                current_sphere = self.zones_data[self.FindZoneByName(zone)].sphere
                if current_sphere != 0:
                    sphere_counter[current_sphere - 1] = sphere_counter[current_sphere - 1] - 1
                if self.zones_data[self.FindZoneByName(zone)].capital:
                    nCapitals[i] += 1
            nSpheres[i]=sphere_counter.count(0)
        return (nSpheres,nCapitals)

    def ListTurnDeck(self):
        print("The 'secret' turn deck order is:\n")
        for p in self.turn_deck:
            print("{}\n".format(p))
        return 0

    def ExecutePlayersTurn(self):
        current_player_id = self.turn_deck[0]
        print("Now is {}'s turn.\n".format(self.players[current_player_id].name))
        print("You can (1)move/attack or (2)pass:")
        #->Allow some selection action
        option = 1
        if option == 1:
            #->Allow some selection of zones to move
            (origin,destination) = self.AI_ChooseRandomTerrainsToMove(current_player_id)
            self.MoveArmyIfTerrainAllows(current_player_id,origin,destination,1)
        if option == 2:
            pass
        self.turn_deck.pop(0)
        return current_player_id

    def ExecutePlayersMovilization(self):
        current_player_id = self.movilization_order[0]
        #->Count other bonuses (cards)
        (prod, nSph, nCap) = self.CalculateProdSpheCaps()
        bonus = 0
        total_units = 2 + math.floor(prod[current_player_id]/3) + nSph[current_player_id] + nCap[current_player_id]
        print("It's {}'s turn to movilize units! You have {} unit(s) left to place\n".format(self.players[current_player_id].name,total_units))
        while total_units > 0:
            #->Allow some selection
            zone = self.AI_ChooseRandomTerrainToReinforce(current_player_id)
            number_of_units = randint(1, total_units)
            self.addToPlayerArmy(current_player_id,zone,number_of_units)
            total_units -= number_of_units
            print("{} unit(s) placed in {}. You have {} units left to place".format(number_of_units,zone,total_units))
        self.movilization_order.pop(0)
        return current_player_id

    def AI_ChooseRandomTerrainToReinforce(self,player_id):
        player_zones = list(self.players[player_id].army.keys())
        possible_zones = []
        for x in player_zones:
            if self.zones_data[self.FindZoneByName(x)].sphere != 0:
                possible_zones.append(x)
        zone = possible_zones[randint(0, len(possible_zones) - 1)]
        return zone

    def AI_ChooseRandomTerrainsToMove(self,player_id):
        player_zones = list(self.players[player_id].army.keys())
        possible_origins = []
        for x in player_zones:
            if self.players[player_id].army[x] > 1:
                possible_origins.append(x)
        origin = possible_origins[randint(0, len(possible_origins) - 1)]
        origin_ID = self.FindZoneByName(origin)
        possible_destinations = self.ZoneConnections(origin_ID)
        destination = possible_destinations[randint(0, len(possible_destinations) - 1)]
        return (origin,destination)

        
            
