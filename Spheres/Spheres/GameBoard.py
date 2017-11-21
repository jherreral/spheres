class Zone:
    def __init__(self, **kwargs):
        nodeID = None
        noneName = None
        sphere = None
        production = None
        petrol = None
        interest = None
        capital = None
        return super().__init__(**kwargs)

class GameBoard:
    def __init__(self, **kwargs):
        round = None
        zones_data = []
        edges_pairs = None
        turn_deck = None
        return super().__init__(**kwargs)
