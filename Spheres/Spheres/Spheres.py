import GameBoard
from random import randint

#Loading data
theBoard = GameBoard.GameBoard()
theBoard.DataBoardParse()
theBoard.EdgeParse()

#Setting the board
theBoard.PopulateAvailableCapitals()
theBoard.CreatePlayers(4)
people = list(theBoard.players.keys())
for p in people:
    theBoard.players[p].ListArmy()

#First players actions
origin = theBoard.players[people[0]].capital
origin_ID = theBoard.FindZoneByName(origin)
possible_destinations = theBoard.ZoneConnections(origin_ID)
destination = possible_destinations[randint(0, len(possible_destinations) - 1)]
theBoard.MoveArmyIfTerrainAllows(people[0],origin,destination,1)
theBoard.players[people[0]].ListArmy()

