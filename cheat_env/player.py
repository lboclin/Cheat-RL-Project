class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
    
    def receive_card(self, card):
        self.hand.append(card)

    def __repr__(self):
        return f"{self.name} has {len(self.hand)} cards."
    