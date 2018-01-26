import queue

class Selection:
    def __init__(self, options, typeOfSelection):
        self.options = options
        self.selection = None
        self.typeOfSelection = typeOfSelection

    def setSelection(self,select):
        self.selection = select

    def sendSelection(self,queue):
        response = Selection(self.options,self.typeOfSelection)
        response.setSelection(self.selection)
        queue.put(response)
