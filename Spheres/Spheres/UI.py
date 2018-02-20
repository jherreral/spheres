import pygame,sys,os
import GameBoard
from Selection import Selection
import queue
import threading
from copy import deepcopy


class UI:
    def __init__(self, receiveQueue, sendQueue, cardQueue):
        self.imageBank = {}
        self.turnImages = {}
        self.specialImages = {}
        self.startingImages = {}
        self.diceImages = {}
        self.theBoard = None
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue
        self.cardQueue = cardQueue
        self.targetFramerate = 60
        self.fonts = []
        self.factionColors = []

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

        self.imageBank["UI"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\UI",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\UI\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["UI"][name] = pygame.image.load(path)

        self.imageBank["MP"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Map",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Map\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["MP"][name] = pygame.image.load(path)
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
        if "UI_"+name in self.imageBank["UI"]:
            return "UI_"+name
        if "MP_"+name in self.imageBank["MP"]:
            return "MP_"+name
        return False

    def startUI(self):
        pygame.init()
        pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.ACTIVEEVENT])
        size = width, height = 1360, 768
        #speed = [2, 2]
        black = 0, 0, 0
        self.fonts.append(pygame.font.SysFont('Courier New', 30))
        self.fonts.append(pygame.font.SysFont('Helvetica',30,True))
        self.factionColors = [(255,0,0),(255,204,0),(204,204,204),(0,0,255),(0,80,0),(204,0,255),(0,0,0),(128,51,0)]
        self.screen = pygame.display.set_mode(size)

        self.CreatePanels()

        boardReady = False
        while not boardReady:
            if not self.receiveQueue.empty():
                self.GB_getInfoAndUpdate(self.receiveQueue.get())
                boardReady = True

    def CreatePanels(self):
        theUI = self
        self.objectList.append(UI_Map(theUI,260,0,827,568,(0,0,150)))
        self.objectList.append(UI_PlayerCards(theUI,0,0,260,568,(0,100,0)))
        self.objectList.append(UI_SpecialDeck(theUI,0,568,260,200,(220,120,0)))
        self.objectList.append(UI_Hand(theUI,260,568,827,200,(0,120,0)))

    def pollQueue(self):
        while not self.receiveQueue.empty():
            somethingFromGB = self.receiveQueue.get()
            typeOfObject = type(somethingFromGB)
            if typeOfObject is Selection:
                typeOfSelection = somethingFromGB.typeOfSelection
                if typeOfSelection == "Card":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,"Card",self,50,50,640,480,(100,100,0)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "Pause":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,"Pause",self,450,450,200,200,(0,0,100)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "DiceSelection":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,"DiceSelection",self,400,400,200,200,(0,0,100),True))
                    self.receiveQueue.task_done()
                if typeOfSelection == "CardTime":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,"Pause",self,450,450,200,200,(0,0,100)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "Map":
                    self.objectList.append(SelectionMap(somethingFromGB.options,typeOfSelection,self.objectList[0],self,260,0,827,568,(100,0,0)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "MoveAttack":
                    self.objectList.append(SelectionTurn(somethingFromGB.options,typeOfSelection,self.objectList[0],self,260,0,827,568,(100,0,0)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "2ndSeaMove":
                    self.objectList.append(SelectionTurn(somethingFromGB.options,typeOfSelection,self.objectList[0],self,260,0,827,568,(100,0,0),True))             
                    self.receiveQueue.task_done()
                if typeOfSelection == "AttackingDice":
                    combatPanelExists = False
                    for panels in self.objectList:
                        if type(panels) == UI_CombatPanel:
                            combatPanelExists = True
                    if combatPanelExists:
                        self.combatPanel.maxUnits = somethingFromGB.options
                    else:
                        self.objectList.append(UI_CombatPanel(self,100,200,200,400,(20,20,20),somethingFromGB.options))
                        self.combatPanel = self.objectList[len(self.objectList) - 1]
                    self.combatPanel.AttackingDice()
                    self.receiveQueue.task_done()
                if typeOfSelection == "EndCombat":
                    self.combatPanel.EndCombat()
                    self.receiveQueue.task_done()
                if typeOfSelection == "ConquestAmount":
                    self.combatPanel.ConquestAmount(somethingFromGB.options)
                    self.receiveQueue.task_done()
                if typeOfSelection == "KeepAttacking":
                    self.combatPanel.KeepAttacking()
                    self.receiveQueue.task_done()
                if typeOfSelection == "Mobiliz":
                    self.objectList.append(SelectionMobiliz(somethingFromGB.options,typeOfSelection,self.objectList[0],self,260,0,827,568,(100,0,0)))
                    self.receiveQueue.task_done()
            if typeOfObject is GameBoard.GameBoard:
                self.GB_getInfoAndUpdate(somethingFromGB)

    def GB_getInfoAndUpdate(self,GBreceived):
        self.theBoard = GBreceived
        self.objectList[0].GB_getNumberOfUnitsInZones()
        self.objectList[1].GB_getCardsFromGameBoard()
        self.objectList[2].GB_getNewTopCard()
        self.receiveQueue.task_done()

    def update(self):
        self.pollQueue()
        if pygame.event.peek(pygame.QUIT):
            self.objectList.clear()
            pygame.quit()
            return True
        mouseButtonUpEvents = pygame.event.get(pygame.MOUSEBUTTONUP)
        mouseButtonDownEvents = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        priorityPanelList = []
        if mouseButtonDownEvents:
            lastMouseButtonEvent = mouseButtonDownEvents[len(mouseButtonDownEvents)-1]
            for panel in self.objectList:
                if panel.myRect.collidepoint(lastMouseButtonEvent.pos[0],lastMouseButtonEvent.pos[1]):
                    panel.pressed(lastMouseButtonEvent)

        #Start drawing
        self.screen.fill((0,0,0))
        for i in self.objectList:
            if i.jobDone:
                self.objectList.remove(i)
                continue
            i.update()
        pygame.display.flip()
        return False

class UI_Panel:
    def __init__(self, UI, left, top, width, height, background):
        self.theUI = UI
        self.background = background
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.jobDone = False
        self.blocked = False
        self.objectList = []
        self.myRect = pygame.Rect(self.left,self.top,self.width,self.height)

    def updateBlocked():
        blockLayer = pygame.Surface((self.myRect.width,self.myRect.height))
        blockLayer.fill((0,0,0))
        blockLayer.set_alpha(50)
        self.theUI.screen.blit(blockLayer,self.myRect)

    def pressed(self,event):
        for object in self.objectList:
            if type(object) == UI_Button or type(object) == UI_Panel:
                if object.myRect.collidepoint(event.pos[0],event.pos[1]):
                    object.pressed()
 
class MP_Zone():
    def __init__(self, name, surf, rect, position, mask):
        self.name = name
        self.surf = surf
        self.rect = rect
        self.position = position
        self.mask = mask
        self.units = None

    def copy(self):
        return MP_Zone(self.name,self.surf.copy(),self.rect.copy(),self.position,self.mask)


class UI_Map(UI_Panel):
    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)
        self.map = self.theUI.imageBank["MP"]["MP_Board"]
        self.map = pygame.transform.scale(self.map,(self.width,self.height))
        self.objectList = []
        self.ParseZones()

    def ParseZones(self):
        f = open("MapCoords.csv","r")
        for line in f:
            (name,x,y) = line.split(";")
            x = int(x)
            y = int(y.rstrip())
            surf = self.theUI.imageBank["MP"]["MP_"+name]
            rect = surf.get_rect()
            rect.move_ip(x,y)
            self.objectList.append(MP_Zone(name,surf,rect,(x,y),pygame.mask.from_surface(surf)))
        f.close()

    def generateNumber(self,number,color):
        if number == 0:
            return pygame.Surface((0,0))
        return self.theUI.fonts[1].render(str(number), False, color)

    def getSurfaceOfNumberFromFontImage(self,number,color):
        if number == 0:
            return pygame.Surface((0,0))
        return self.theUI.imageBank["UI"]["numbers"].subsurface(pygame.Rect(48*(number-1),28*color,48,28))

    def getPlayerColor(self,faction):
        colors = {'Total':0,'Milit':1,'Inter':2,'Democ':3,'Dynas':4,'Theoc':5,'Commu':6,'Calip':7}
        return self.theUI.factionColors[colors[faction]]

    def GB_getNumberOfUnitsInZones(self):
        for mapzone in self.objectList:
            set = False
            for player in self.theUI.theBoard.players:
                if set:
                    break
                for zonename in player.army:
                    if set:
                        break
                    if zonename == mapzone.name:
                        mapzone.units = self.generateNumber(player.army[zonename],self.getPlayerColor(player.faction))
                        set = True
            if not set:
                mapzone.units = pygame.Surface((0,0))
                set = True

    def update(self):
        self.theUI.screen.blit(self.map,self.myRect)
        mPos = pygame.mouse.get_pos()
        for zone in self.objectList:
            maskSize = zone.mask.get_size()
            centering = ((maskSize[0] - zone.units.get_width())/2, (maskSize[1] - zone.units.get_height())/2)
            offset_position = (centering[0] + zone.position[0] + self.left, centering[1] + zone.position[1] + self.top)
            self.theUI.screen.blit(zone.units,offset_position)
            
            maskX = mPos[0]-zone.position[0]-self.left
            maskY = mPos[1]-zone.position[1]-self.top
            if maskX in range(0,maskSize[0]) and maskY in range(0,maskSize[1]):
                if zone.mask.get_at((maskX,maskY)):
                    self.theUI.screen.blit(zone.surf, zone.rect.move(self.left,self.top))

    def pressed(self, event):
        pass

class SelectionMap(Selection, UI_Panel):
    def __init__(self, options, typeOfSelection, map, UI,  left, top, width, height, background):
        Selection.__init__(self,options, typeOfSelection)
        UI_Panel.__init__(self,UI, left, top, width, height, background)
        
        self.theMap = map
        self.objectList = []

        for option in self.options:
            for zone in self.theMap.objectList:
                if zone.name == option:
                    self.objectList.append(zone.copy())
        color = (200,200,0)
        for zone in self.objectList:
            zone.surf.fill(color,None,pygame.BLEND_RGB_MULT)

    def update(self):
        if not self.selection == None:
            self.sendSelection(self.theUI.sendQueue)
            self.jobDone = True
            return

        for zone in self.objectList:
            self.theUI.screen.blit(zone.surf,zone.rect.move(self.theMap.left,self.theMap.top))

    def pressed(self, event):
        mPos = event.pos
        for zone in self.objectList:
            maskSize = zone.mask.get_size()
            maskX = mPos[0]-zone.position[0]-self.left
            maskY = mPos[1]-zone.position[1]-self.top
            if maskX in range(0,maskSize[0]) and maskY in range(0,maskSize[1]):
                if zone.mask.get_at((maskX,maskY)):
                    self.selection = zone.name
   

class SelectionTurn(Selection, UI_Panel):
    def __init__(self, options, typeOfSelection, map, UI, left, top, width, height, background, seaMove = False):
        Selection.__init__(self,options, typeOfSelection)
        UI_Panel.__init__(self,UI, left, top, width, height, background)

        self.theMap = map
        self.objectList = []
        self.pressableList = []
        self.selectedOrigin = None
        self.n = 1
        self.maxUnitsToMove = self.options[1]
        self.panelList = []
        self.buttonList = []
        self.color1 = (200,200,0)
        self.color2 = (250,250,0)

        if seaMove:
            self.pressableList = self.objectList
            self.panelList.append(UI_AmountPanel(self.theUI,550,400,100,300,(0,0,0),self.options[1]))
            self.SetupDestinationSelection(self.options[0][0].typeOfSelection,self.options[0][0])
        else:
            for selectionObject in self.options:
                for zone in self.theMap.objectList:
                    if zone.name == selectionObject.typeOfSelection:
                        self.objectList.append((selectionObject,zone.copy()))
            for dummy,zone in self.objectList:
                zone.surf.fill(self.color1,None,pygame.BLEND_RGB_MULT)
            self.pressableList = self.objectList

    def update(self):
        if not self.selection == None:
            self.sendSelection(self.theUI.sendQueue)
            self.jobDone = True
            return

        for dummy,zone in self.objectList:
            self.theUI.screen.blit(zone.surf,zone.rect.move(self.theMap.left,self.theMap.top))

        for x in self.panelList:
            x.update()

    def SetupDestinationSelection(self,origin,selectionObject):
        self.selectedOrigin = origin
        self.pressableList.clear() # Limpia ambas listas
        #if type(selectionObject.options) == tuple:
        destinations = selectionObject.options[0] + [self.selectedOrigin]
        #else:
            #destinations = selectionObject.options + [self.selectedOrigin]
        for option in destinations:
            for zone in self.theMap.objectList:
                if zone.name == option:
                    self.objectList.append((selectionObject,zone.copy()))
                    self.objectList[len(self.objectList)-1][1].surf.fill(self.color2,None,pygame.BLEND_RGB_MULT)
                    self.pressableList.append((selectionObject,zone.copy()))

    def pressed(self, event):
        mPos = event.pos
        for selectionObject,zone in self.pressableList:
            maskSize = zone.mask.get_size()
            maskX = mPos[0]-zone.position[0]-self.left
            maskY = mPos[1]-zone.position[1]-self.top
            if maskX in range(0,maskSize[0]) and maskY in range(0,maskSize[1]):
                if zone.mask.get_at((maskX,maskY)):
                    if not self.selectedOrigin == None:
                        self.selection = (self.selectedOrigin,zone.name,self.panelList[0].n)
                        break
                    else:
                        self.panelList.append(UI_AmountPanel(self.theUI,550,400,100,300,(0,0,0),selectionObject.options[1]))
                        self.SetupDestinationSelection(zone.name,selectionObject)
                        return

        for button in self.buttonList:
            if button.myRect.collidepoint(event.pos[0],event.pos[1]):
                button.pressed()

        if len(self.panelList) > 0:
            for button in self.panelList[0].objectList:
                if button.myRect.collidepoint(event.pos[0],event.pos[1]):
                    button.pressed()

class SelectionMobiliz(Selection, UI_Panel):
    def __init__(self, options, typeOfSelection, map, UI, left, top, width, height, background):
        Selection.__init__(self,options, typeOfSelection)
        UI_Panel.__init__(self,UI, left, top, width, height, background)

        self.theMap = map
        self.objectList = []
        
        for option in self.options[0]:
            for zone in self.theMap.objectList:
                if zone.name == option:
                    self.objectList.append(zone.copy())
        color = (200,200,0)
        for zone in self.objectList:
            zone.surf.fill(color,None,pygame.BLEND_RGB_MULT)

        self.panel = UI_AmountPanel(self.theUI,self.left,self.top + 300,100,150,(50,50,50),options[1], False)

    def update(self):
        if not self.selection == None:
            newSelection = Selection(None,"Mobiliz", (self.selection, self.panel.n))
            newSelection.sendSelection(self.theUI.sendQueue)
            self.jobDone = True
            return

        for zone in self.objectList:
            self.theUI.screen.blit(zone.surf,zone.rect.move(self.theMap.left,self.theMap.top))

        self.panel.update()

    def pressed(self, event):
        mPos = event.pos
        for zone in self.objectList:
            maskSize = zone.mask.get_size()
            maskX = mPos[0]-zone.position[0]-self.left
            maskY = mPos[1]-zone.position[1]-self.top
            if maskX in range(0,maskSize[0]) and maskY in range(0,maskSize[1]):
                if zone.mask.get_at((maskX,maskY)):
                    self.selection = zone.name

        for button in self.panel.objectList:
            if button.myRect.collidepoint(event.pos[0],event.pos[1]):
                button.pressed()

class UI_AmountPanel(UI_Panel):
    def __init__(self, UI, left, top, width, height, background,maxUnits,startAtMax = True):
        super().__init__(UI, left, top, width, height, background)
        self.objectList.append(UI_Button("Up",self.theUI,0,0,100,50,(self.left,self.top),"UI_Up"))
        self.objectList.append(UI_Button("Down",self.theUI,0,100,100,50,(self.left,self.top),"UI_Down"))
        if startAtMax:
            self.n = maxUnits
        else:
            self.n = 1
        self.maxUnits = maxUnits
        self.text = str(self.n) + "/" + str(self.maxUnits)
        self.textsurface = self.theUI.fonts[0].render(self.text, False, (255, 255, 255))
        self.textOffset = (25,50)

    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        self.theUI.screen.blit(self.textsurface,(self.left + self.textOffset[0],self.top + self.textOffset[1]))
        for button in self.objectList:
            if button.state == 1:
                if button.buttonName == "Up" and self.n < self.maxUnits:
                    self.n += 1
                    self.text = str(self.n) + "/" + str(self.maxUnits)
                    self.textsurface = self.theUI.fonts[0].render(self.text, False, (255, 255, 255))
                if button.buttonName == "Down" and self.n > 1:
                    self.n -= 1
                    self.text = str(self.n) + "/" + str(self.maxUnits)
                    self.textsurface = self.theUI.fonts[0].render(self.text, False, (255, 255, 255))
                button.state = 0
            button.update()
        

class UI_CombatPanel(UI_Panel):
    def __init__(self, UI, left, top, width, height, background, dice):
        super().__init__(UI, left, top, width, height, background)
        
        self.textOffset = (100,150)
        self.maxUnits = dice
        self.minUnits = 1
        self.n = self.maxUnits

    def AttackingDice(self):
        self.mode = 1
        self.objectList.clear()
        self.objectList.append(self.theUI.fonts[0].render(str(self.n), False, (255, 255, 255)))
        self.objectList.append(UI_Button("Up",self.theUI,50,100,100,50,(self.left,self.top),"UI_Up"))
        self.objectList.append(UI_Button("Down",self.theUI,50,200,100,50,(self.left,self.top),"UI_Down"))
        self.objectList.append(UI_Button("Ready",self.theUI,50,300,100,50,(self.left,self.top),"UI_Ready"))
        self.n = self.maxUnits
        self.objectList[0] = self.theUI.fonts[0].render(str(self.n), False, (255, 255, 255))

    def EndCombat(self):
        self.mode = 2
        self.objectList.clear()
        self.objectList.append(UI_Button("Close",self.theUI,50,200,100,50,(self.left,self.top),"Close"))

    def ConquestAmount(self,minMaxUnits):
        self.mode = 4
        (self.minUnits,self.maxUnits) = minMaxUnits
        self.objectList.pop()
        self.objectList.append(UI_Button("ConquerBtn",self.theUI,50,300,100,50,(self.left,self.top),"Conquer"))
        self.n = self.maxUnits
        self.objectList[0] = self.theUI.fonts[0].render(str(self.n), False, (255, 255, 255))
        #Crear texto en panel
        pass

    def KeepAttacking(self):
        self.mode = 8
        self.objectList.clear()
        self.objectList.append(UI_Button("Attack",self.theUI,0,250,100,50,(self.left,self.top),"Attack"))
        self.objectList.append(UI_Button("Close",self.theUI,100,250,100,50,(self.left,self.top),"Close"))

    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        for obj in self.objectList:
            if type(obj) == pygame.Surface:
                self.theUI.screen.blit(obj,(self.left + self.textOffset[0],self.top + self.textOffset[1]))
                continue
            if obj.state == 1:
                if obj.buttonName == "Up":
                    if (self.mode & 5) != 0 and self.n < self.maxUnits or (self.mode & 5) == 0:
                        self.n += 1
                        self.objectList[0] = self.theUI.fonts[0].render(str(self.n), False, (255, 255, 255))
                elif obj.buttonName == "Down":
                    if (self.mode & 5) != 0 and self.n > self.minUnits or (self.mode & 5) == 0:
                        self.n -= 1
                        self.objectList[0] = self.theUI.fonts[0].render(str(self.n), False, (255, 255, 255))
                elif obj.buttonName == "Close":
                    auxSelection = Selection(None,"EndCombat")
                    auxSelection.selection = None
                    auxSelection.sendSelection(self.theUI.sendQueue)
                    self.jobDone = True
                elif obj.buttonName == "ConquerBtn":
                    auxSelection = Selection(None,"ConquestAmount")
                    auxSelection.selection = self.n
                    auxSelection.sendSelection(self.theUI.sendQueue)
                    self.jobDone = True
                elif obj.buttonName == "Attack":
                    auxSelection = Selection(None,"KeepAttacking")
                    auxSelection.selection = True
                    auxSelection.sendSelection(self.theUI.sendQueue)
                else:
                    auxSelection = Selection(self.maxUnits,"AttackingDice")
                    auxSelection.selection = self.n
                    auxSelection.sendSelection(self.theUI.sendQueue)
                obj.state = 0
            obj.update()


class UI_SpecialDeck(UI_Panel):
    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)
        self.objectList.append(UI_Button("specialDeckBtn",self.theUI,74,50,57,79,(self.left,self.top),"S_BACK"))

    def GB_getNewTopCard(self):
        if len(self.theUI.theBoard.discard_deck) > 0:
            buttonImage = self.theUI.theBoard.discard_deck[0]
            #self.topDiscardDeck = pygame.transform.scale()

    def update(self):
        ### Actualiza y dibuja el panel y sus elementos. Cada elemento llama a su propio update y draw.
        
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        for object in self.objectList:
            object.update()
  
class UI_Button:
    def __init__(self,buttonName,UI,left,top,width,height,ref,imageName,held = False):
        self.buttonName = buttonName
        self.theUI = UI
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.held = held
        self.state = 0

        splittedName = imageName.split("_")
        if len(splittedName) > 1:
            (typeOfImage,image) = splittedName
        else:
            typeOfImage = "Local"
            image = splittedName[0]
        self.screenLeft = self.left + ref[0]
        self.screenTop = self.top + ref[1]

        self.myRect = pygame.Rect(self.screenLeft,self.screenTop,self.width,self.height)
        if not self.theUI.FindImage(image):
            self.buttonOff = pygame.Surface((self.width,self.height))
            self.buttonHighlight = self.buttonOff.copy()
            self.buttonOn = self.buttonOff.copy()
            self.buttonOff.fill((120,120,120))
            self.buttonHighlight.fill((160,160,160))
            self.buttonOn.fill((200,200,200))
            textSurface = self.theUI.fonts[0].render(image, False, (0, 0, 0))
            self.buttonOff.blit(textSurface,(0,0))
            self.buttonHighlight.blit(textSurface,(0,0))
            self.buttonOn.blit(textSurface,(0,0))
        else:
            #self.buttonOff = pygame.transform.scale(self.theUI.imageBank[typeOfImage][typeOfImage+"_"+image+"Off"],(self.width,self.height))
            #self.buttonHighlight = pygame.transform.scale(self.theUI.imageBank[typeOfImage][typeOfImage+"_"+image+"Highlight"],(self.width,self.height))
            self.buttonOn = pygame.transform.scale(self.theUI.imageBank[typeOfImage][typeOfImage+"_"+image],(self.width,self.height))
            
            self.buttonOff = self.buttonOn.copy()
            self.buttonHighlight = self.buttonOn.copy()
            OffSurface = pygame.Surface((self.width,self.height))
            OffSurface.fill((0,0,0))
            OffSurface.set_alpha(50)
            HlSurface = pygame.Surface((self.width,self.height))
            HlSurface.fill((255,255,255))
            HlSurface.set_alpha(50)
            self.buttonOff.blit(OffSurface,(0,0))
            self.buttonHighlight.blit(HlSurface,(0,0))
        
    def drawOff(self):
        self.theUI.screen.blit(self.buttonOff, self.myRect)

    def drawHighlight(self):
        self.theUI.screen.blit(self.buttonHighlight, self.myRect)

    def drawOn(self):
        self.theUI.screen.blit(self.buttonOn, self.myRect)

    def pressed(self):
        if self.held:
            self.state = 0 if self.state == 1 else 1
        else:
            self.state = 1

    def update(self):
        if self.state == 1:
            if not pygame.event.get(pygame.MOUSEBUTTONUP) or self.held == True:
                self.drawOn()
            else:
                self.state = 0
                if self.myRect.collidepoint(pygame.mouse.get_pos()):
                    self.drawHighlight()
                else:
                    self.drawOff()
        else:
            if self.myRect.collidepoint(pygame.mouse.get_pos()):
                self.drawHighlight()
            else:
                self.drawOff()
            

class SelectionPanel(Selection,UI_Panel):
    def __init__(self, options, typeOfSelection, UI, left, top, width, height, background, multi = False):
        Selection.__init__(self,options,typeOfSelection)
        UI_Panel.__init__(self,UI, left, top, width, height, background)
        
        self.multi = multi
        
        if typeOfSelection == "Card":
            nOpts = len(self.options)
            self.width = 200+nOpts*378
            self.height = 50+526
            self.myRect.inflate_ip(self.width - self.myRect.width,self.height - self.myRect.height)
            for i,objectName in enumerate(self.options):
                self.objectList.append(UI_Button(objectName,self.theUI,100+i*378,50,378,526,(self.left,self.top),self.theUI.FindImage(objectName)))

        if typeOfSelection == "Pause":
            self.width = 200
            self.height = 200
            self.myRect.inflate_ip(self.width - self.myRect.width,self.height - self.myRect.height)
            self.objectList.append(UI_Button("Pause",self.theUI,10,10,180,180,(self.left,self.top),"PauseASDF"))
        
        if typeOfSelection == "DiceSelection":
            nOpts = len(self.options)
            self.left = 400
            self.top = 500
            self.width = max(10+nOpts*50,100)
            self.height = 110
            self.myRect = pygame.Rect(self.left,self.top,self.width,self.height)
            for idx,dice in enumerate(self.options):
                self.objectList.append(UI_Button("dice"+str(idx),self.theUI,10+idx*50,10,40,40,(self.left,self.top),str(dice), True))
            self.objectList.append(UI_Button("Confirmacion",self.theUI,10,60,100,40,(self.left,self.top),"Confirmar"))
        else:
            self.width = 300
            self.height = 300

    def update(self):
        ### Actualiza y dibuja el panel de sUI_Paneleleccion y sus elementos. Cada elemento llama a su propio update y draw.
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        if self.multi:
            if self.objectList[len(self.objectList)-1].state == 1:
                aux_selec = Selection(None,"DiceSelection")
                self.objectList.pop()
                aux_list = []
                for idx,dice in enumerate(self.objectList):
                    if dice.state == 0:
                        aux_list.append(self.options[idx])
                aux_selec.setSelection(aux_list)
                aux_selec.sendSelection(self.theUI.sendQueue)
                self.jobDone = True
                return

        for button in self.objectList:
            if button.state == 1 and not self.multi:
                self.selection = button.buttonName
                self.sendSelection(self.theUI.sendQueue)
                self.jobDone = True
                return
            button.update()

class SelectQuantityPanel(Selection, UI_Panel):
    def __init__(self, options, typeOfSelection, UI, left, top, width, height, background):
        Selection.__init__(self,options,typeOfSelection)
        UI_Panel.__init__(self,UI, left, top, width, height, background)

        nOpts =len(self.options)
        ### PENDIENTE: Terminar esta clase

class UI_Track(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

    def update(self):
        pass

class UI_PlayerCards(UI_Panel):
    def __init__(self, UI, left, top, width, height, background):
        UI_Panel.__init__(self,UI, left, top, width, height, background)

        self.playerHands = []
        self.objectList = []

    def GB_getCardsFromGameBoard(self):
        self.playerHands.clear()
        self.objectList.clear()
        for idx,player in enumerate(self.theUI.theBoard.players):
            hand = []
            for card in player.hand:
                hand.append(card)
            self.playerHands.append((player.name,hand))
            self.objectList.append(UI_Button(player.name,self.theUI,10,10+60*idx,50,50,(self.left,self.top),str(len(hand))))
    
    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        for idx,button in enumerate(self.objectList):
            if button.state == 1:
                self.theUI.objectList[3].loadNewHand(self.playerHands[idx])
                button.state = 0
            button.update()
        
class UI_Hand(UI_Panel):
    def __init__(self, UI, left, top, width, height, background):
        UI_Panel.__init__(self,UI, left, top, width, height, background)

        self.owner = None
        self.textsurface = self.theUI.fonts[0].render("No Cards in Hand", False, (255, 255, 255))
        self.objectList = []

    def loadNewHand(self,ownerHandPair):
        (self.owner,handToLoad) = ownerHandPair
        self.objectList.clear()
        self.textsurface = self.theUI.fonts[1].render(self.owner, False, (0, 0, 0))
        for idx,card in enumerate(handToLoad):
            self.objectList.append(UI_Button(card,self.theUI,20+70*idx,20,50,100,(self.left,self.top),self.theUI.FindImage(card)))
        
    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        self.theUI.screen.blit(self.textsurface,(20 + self.left, 120 + self.top))
        for button in self.objectList:
            if button.state == 1:
                self.theUI.cardQueue.put((button.buttonName,self.owner))
                button.state = 0
            button.update()