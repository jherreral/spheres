import pygame,sys,os
import GameBoard
from Selection import Selection
import threading
import queue

class SelectionUI(Selection):
    def __init__(self, options, type, UI):
        super().__init__(options, type)
        
        self.theUI = UI
        self.objectList = []
        self.background = 100,100,0
        self.left = 50
        self.top = 50

        nOpts = len(self.options)
        if type == "Card":
            self.width = 200+nOpts*378
            self.height = 50+nOpts*526
        else:
            self.width = 300
            self.height = 300

        for i,objectName in enumerate(self.options):
            self.objectList.append(UI_Button(objectName,self.theUI,100+i*378,50,378,526,self.theUI.FindImage(objectName)))

    def update(self):
        ### Actualiza y dibuja el panel de seleccion y sus elementos. Cada elemento llama a su propio update y draw.
        pygame.draw.rect(self.theUI.screen, self.background, [self.left, self.top, self.width, self.height])
        for thing in self.objectList:
            thing.update((self.left,self.top))
        pygame.display.flip()



class SelectionPlayer(SelectionUI):
    def ShowSelection():
        pass

class SelectionCard(SelectionUI):
    def ShowSelection():
        pass

class SelectionDice(SelectionUI):
    def ShowSelection():
        pass 

class UI:
    def __init__(self, receiveQueue, sendQueue):
        self.imageBank = {}
        self.turnImages = {}
        self.specialImages = {}
        self.startingImages = {}
        self.diceImages = {}
        self.theBoard = None
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue
        
        self.screen = None

        self.objectList = []

    def loadImages(self):
        cwd = os.getcwd()
        self.imageBank["S"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Special",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Special\\" + filename
                self.specialImages[name] = pygame.image.load(path)
                self.imageBank["S"][name] = pygame.image.load(path)
        
        self.imageBank["SL"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\StartingLocations",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\StartingLocations\\" + filename
                self.startingImages[name] = pygame.image.load(path)
                self.imageBank["SL"][name] = pygame.image.load(path)

        self.imageBank["T"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Turn",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Turn\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["T"][name] = pygame.image.load(path)
        #imagerect = self.specialImages["S_AirSu"].get_rect()
        #while 1:
        #    red = 250,0,0
        #    black = 0,0,0
        #    self.screen.fill(black)
        #    self.screen.blit(self.specialImages["S_AirSu"], imagerect)
        #    pygame.display.flip()
        return 0

    def FindImage(self,name):
        if "S_"+name in self.imageBank["S"]:
            return "S_"+name
        #self.imageBank["S"]["S_"+name]
        if "SL_"+name in self.imageBank["SL"]:
            return "SL_"+name
        #self.imageBank["SL"]["SL_"+name]
        if "T_"+name in self.imageBank["T"]:
            return "T_"+name
        #self.imageBank["T"]["T_"+name]


    def startUI(self):
        boardReady = False
        while not boardReady:
            if not self.receiveQueue.empty():
                self.theBoard = self.receiveQueue.get()
                self.receiveQueue.task_done()
                boardReady = True

        pygame.init()

        size = width, height = 1360, 768
        #speed = [2, 2]
        black = 0, 0, 0

        self.screen = pygame.display.set_mode(size)



        #while 1:
        #    for event in pygame.event.get():
        #        if event.type == pygame.QUIT: sys.exit()

        #    ballrect = ballrect.move(speed)
        #    if ballrect.left < 0 or ballrect.right > width:
        #        speed[0] = -speed[0]
        #    if ballrect.top < 0 or ballrect.bottom > height:
        #        speed[1] = -speed[1]

        #    screen.fill(black)
        #    screen.blit(ball, ballrect)
        #    pygame.display.flip()

    def CreatePanels(self):
        theUI = self
        self.objectList.append(UI_SpecialDeck(theUI,0,540,270,230,(220,120,0)))


    def update(self):
        #Poll queue
        while not self.receiveQueue.empty():
            somethingFromGB = self.receiveQueue.get()
            typeOfObject = type(somethingFromGB)
            if typeOfObject is Selection:
                typeOfSelection = somethingFromGB.type
                if typeOfSelection == "Card":
                    self.objectList.append(SelectionUI(somethingFromGB.options,typeOfSelection,self))
                    self.receiveQueue.task_done()
            if typeOfObject is GameBoard.GameBoard:
                self.theBoard = somethingFromGB
                self.receiveQueue.task_done()
        for i in self.objectList:
            i.update()

class UI_Button:
    def __init__(self,buttonName,UI,left,top,width,height,imageName):
        self.buttonName = buttonName
        self.theUI = UI
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.state = 0

        (type,image) = imageName.split("_")
        
        self.buttonOff = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image+"Off"],(self.width,self.height))
        self.buttonOffRect = pygame.Rect(self.left,self.top,self.width,self.height)
        self.buttonHighlight = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image+"Highlight"],(self.width,self.height))
        self.buttonHighlighRect = pygame.Rect(self.left,self.top,self.width,self.height)
        self.buttonOn = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image],(self.width,self.height))
        self.buttonOnRect = pygame.Rect(self.left,self.top,self.width,self.height)

    def drawOff(self,reference):
        self.theUI.screen.blit(self.buttonOff, self.buttonOffRect.move(reference[0],reference[1]))

    def drawHighlight(self,reference):
        self.theUI.screen.blit(self.buttonOff, self.buttonOffRect.move(reference[0],reference[1]))

    def drawOn(self,reference):
        self.theUI.screen.blit(self.buttonOff, self.buttonOffRect.move(reference[0],reference[1]))

    def update(self,reference):
        #Chech mouse over
        switcher = {
            0: "drawOff",
            1: "drawHighlight",
            2: "drawOn",
        }
        method = getattr(self, switcher[self.state],lambda:"Error")
        #func = switcher.get(self.state, lambda: "Error")
        method(reference)

    

class UI_Panel:
    def __init__(self, UI, left, top, width, height, background):
        self.theUI = UI
        self.background = background
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.objectList = []

class UI_Map(UI_Panel):
    def __init__(self, UI):
        pass

class UI_SpecialDeck(UI_Panel):

    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)
        self.objectList.append(UI_Button("specialDeckBtn",self.theUI,74,50,57,79,"S_BACK"))

    def update(self):
        ### Actualiza y dibuja el panel y sus elementos. Cada elemento llama a su propio update y draw.
        if len(self.theUI.theBoard.discard_deck) > 0:
            buttonImage = self.theUI.theBoard.discard_deck[0]
            #self.topDiscardDeck = pygame.transform.scale()

        pygame.draw.rect(self.theUI.screen, self.background, [self.left, self.top, self.width, self.height])
        for object in self.objectList:
            object.update((self.left,self.top))
        pygame.display.flip()
        


class UI_Hand(UI_Panel):
    
    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)

    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, [self.left, self.top, self.width, self.height])
        self.getCards()
        self.drawCards()

    def getCards(self):
        pass

    def drawCards(self):
        pass

class UI_Track(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

    def update(self):
        pass

class UI_PlayerCards(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

