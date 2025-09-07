from .card import Card, Suit
import random

class Deck:
    def __init__(self):
        values = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        suits = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]
        self.cards = [Card(value, suit) for value in values for suit in suits]
        self.cards.append(Card("Joker", Suit.JOKER))
        self.cards.append(Card("Joker", Suit.JOKER))

    def shuffle (self):
        random.shuffle(self.cards)

    def get_card(self):
        if len(self.cards) != 0:
            return self.cards.pop()
        else:
            return None
        
