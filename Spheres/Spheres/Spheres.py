import GameBoard
import UI
import queue
from random import randint

def UIThread(receiveQueue, sendQueue,cardQueue):
    ### Run UI in this thread
    theUI = UI.UI(receiveQueue, sendQueue,cardQueue)
    theUI.loadImages()
    theUI.startUI()
    UIdone = False
    while not UIdone:
        UIdone = theUI.update()

#Create queue objects for thread communication
ToUI_queue = queue.Queue()
ToGB_queue = queue.Queue()
cardQueue = queue.Queue()

#Loading data
theBoard = GameBoard.GameBoard(ToGB_queue, ToUI_queue, cardQueue)
theBoard.LoadData()

#Start UI thread
UI_thread = UI.threading.Thread(target=UIThread, args=(ToUI_queue,ToGB_queue,cardQueue,))
UI_thread.daemon = True
UI_thread.start()

#Setting the board
#theBoard.BoardSetup(4)
theBoard.AI_LoadScenario()

theBoard.UpdateBoardForUI()

theBoard.GameLoop()

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


