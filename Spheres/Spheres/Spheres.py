import GameBoard
import UI
import queue
from random import randint

def UIThread(receiveQueue, sendQueue):
    ### Run UI in this thread
    theUI = UI.UI(receiveQueue, sendQueue)
    theUI.loadImages()
    theUI.CreatePanels()
    theUI.startUI()
    UIdone = False
    while not UIdone:
        UIdone = theUI.update()

#Create queue objects for thread communication
ToUI_queue = queue.Queue()
ToGB_queue = queue.Queue()

#Loading data
theBoard = GameBoard.GameBoard(ToGB_queue, ToUI_queue)
theBoard.DataBoardParse()
theBoard.EdgeParse()
theBoard.CalculateZonesPerSphere()
theBoard.FirstBoardForUI()

#Start UI thread
UI_thread = UI.threading.Thread(target=UIThread, args=(ToUI_queue,ToGB_queue,))
UI_thread.daemon = True
UI_thread.start()

#Setting the board
theBoard.PopulateAvailableCapitals()
theBoard.CreatePlayers(4)
for i in range(len(theBoard.players)):
    theBoard.players[i].ListArmy()

theBoard.AI_LoadScenario()
theBoard.UpdateBoardForUI()
while theBoard.round < 6:
    theBoard.round += 1

    theBoard.ArrangeMovilizationDeck()
    while len(theBoard.movilization_order) > 0:
        current_player = theBoard.ExecutePlayersMovilization()
        theBoard.players[current_player].ListArmy()

    theBoard.ArrangeTurnDeck()
    while len(theBoard.turn_deck) > 0:
        current_player = theBoard.ExecutePlayersTurn()
        theBoard.players[current_player].ListArmy()


