class Selection:
    def __init__(self, options, type):
        self.options = options
        self.selection = None
        self.type = type

    def setSelection(self,select):
        self.selection = select
