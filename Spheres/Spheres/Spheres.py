import GameBoard
from random import randint

#Loading data
theBoard = GameBoard.GameBoard()
theBoard.DataBoardParse()
theBoard.EdgeParse()
theBoard.CalculateZonesPerSphere()

#Setting the board
theBoard.PopulateAvailableCapitals()
theBoard.CreatePlayers(4)
for i in range(len(theBoard.players)):
    theBoard.players[i].ListArmy()
theBoard.ArrangeTurnDeck()
theBoard.ListTurnDeck()

#First players actions
while len(theBoard.turn_deck) > 0:
    current_player = theBoard.ExecutePlayersTurn()
    theBoard.players[current_player].ListArmy()

#First reinforcement
(nSpheres,nCaps,_) = theBoard.CheckSpheres()
theBoard.ArrangeMovilizationDeck()
while len(theBoard.movilization_order) > 0:
    current_player = theBoard.ExecutePlayersMovilization()
    theBoard.players[current_player].ListArmy()

theBoard.AI_LoadScenario()

