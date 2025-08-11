from enum import Enum

class Suit(Enum):
    SPADES = "Spades"
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    JOKER = "Joker"

class Card:
    def __init__ (self, value : str, suit : Suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        if self.suit == Suit.JOKER:
            return f"Joker"
        return f"{self.value} of {self.suit.value}"