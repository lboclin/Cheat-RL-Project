from .card import Card, Suit
from .deck import Deck
from .player import Player
import numpy as np


class CheatEnviroment:

    def __init__(self, players_names: list):
        if len(players_names) < 2:
            raise ValueError("The game need at least 2 players.")

        print("Setting up the table with the players...")
        self.players = [Player(name) for name in players_names]


        self.rl_agent = self.players[0] # Define the RL agent as the first player
        self.deck = None
        self.current_player_index = 0
        self.current_rank_to_play = None
        self.last_player_who_played_index = None
        self.round_discard_pile = []
        self.pass_counter = 0
        self.winner = None
        self.starter_player_index = None




    def _get_state(self):

        current_player = self.players[self.current_player_index]
    
        # List of the card values
        card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        value_to_index = {value: i for i, value in enumerate(card_values)}

        # 1. Current player hand
        hand_vector = np.zeros(14)
        for card in current_player.hand:
            if card.value in value_to_index: # Verifica se o valor é válido
                hand_vector[value_to_index[card.value]] += 1
        
        # 2. Number of opponents cards
        opponent_card_counts = [len(p.hand) for p in self.players if p is not current_player]

        # 3. Round card
        rank_vector = np.zeros(14)
        if self.current_rank_to_play in value_to_index:
            rank_vector[value_to_index[self.current_rank_to_play]] = 1

        # 4. Other game information
        discard_pile_size = [len(self.round_discard_pile)]
        if self.starter_player_index == None :
            is_starting_play = [0.0]
        else :
            is_starting_play = [1.0]

        
        # Concatenate everything
        state_vector = np.concatenate([
            hand_vector,
            np.array(opponent_card_counts),
            rank_vector,
            np.array(discard_pile_size),
            np.array(is_starting_play)
        ]).astype(np.float32)
        
        return state_vector 
    


    def get_valid_actions(self):
        """
        Analyzes the current game state and returns a dictionary of legal actions
        for the current player. This is crucial for the agent's action masking.
        """
        valid_actions = {
            "types": [],
            "ranks": [],
            "quantities": [],
            "is_starter": False,
            "current_rank": self.current_rank_to_play,
            "player_hand": self.players[self.current_player_index].hand
        }
        
        current_player = self.players[self.current_player_index]
        is_starter = (self.starter_player_index == self.current_player_index)
        valid_actions["is_starter"] = is_starter

        # --- Determine valid action types ---
        if is_starter:
            valid_actions["types"].append(2) # Must play
        else:
            valid_actions["types"] = [0, 1, 2]

        # --- Determine valid ranks and quantities for a 'Play' action ---
        # Agent can always announce any rank if it's the starter
        if is_starter:
            valid_actions["ranks"] = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        
        # Agent can play from 1 up to the number of cards in their hand (capped at 6)
        max_qty = min(len(current_player.hand), 6)
        if max_qty > 0:
            valid_actions["quantities"] = list(range(max_qty)) # 0-5, which corresponds to 1-6 cards

        return valid_actions



    def _deal_cards(self):
        print("Creating and shuffling a new deck...")

        # Initialize and shuffle the deck
        self.deck = Deck()
        self.deck.shuffle()

        # Clean the last player's hands
        for player in self.players:
            player.hand = []

        print("Dealing cards...")

        # Deal cards while the deck is not empty
        card_to_deal = self.deck.get_card()
        player_index = 0
        while card_to_deal is not None:
            self.players[player_index % len(self.players)].receive_card(card_to_deal)
            card_to_deal = self.deck.get_card()
            player_index += 1



    def check_game_over(self):
        for player in self.players:
            if len(player.hand) == 0:
                self.winner = player 
                return True
        return False
    


    def reset(self):
        print("\n--- GAME STARTING ---")

        self._deal_cards() # Deal cards
        self.current_player_index = 0
        self.current_rank_to_play = None
        self.starter_player_index = None
        self.last_player_who_played_index = None
        self.last_number_of_cards_played = None
        self.round_discard_pile = []
        self.pass_counter = 0

        # Initialize the first round
        self._start_new_round(self.current_player_index)

        return self._get_state()
 


    def step(self, action: tuple): 
        
        # Unravel the action
        action_type, cards_to_play, announced_rank = action

        # Define the acting player index
        acting_player_index = self.current_player_index
        
        # Define variables
        round_ended_by_challenge = False
        reward = 0.0
        terminated = False

        if action_type == 0:
            # Doubt the last play
            self._resolve_challenge(acting_player_index, self.last_player_who_played_index)
            round_ended_by_challenge = True
        elif action_type == 1:
            # Pass the turn
            self._handle_pass(acting_player_index)
        else:
            # Play cards
            self._play_cards(acting_player_index, cards_to_play, announced_rank)
        

        # Check if the game has finished
        terminated = self.check_game_over()

        if terminated :
            if reward == 0.0 :
                winner = self.players[acting_player_index]
                if winner == self.rl_agent :
                    reward = 1.0
                else :
                    reward = -1.0
            
        if not terminated:
            if self.pass_counter >= (len(self.players)-1):
                print("--- Round Over (All players passed) ---")
                self._start_new_round(self.last_player_who_played_index)
            elif round_ended_by_challenge:
                pass
            else:
                # Define the next player
                if self.starter_player_index == None :
                    self.current_player_index = (self.current_player_index+1) % len(self.players)

        # Return the passing result
        state = self._get_state()
        truncated = False
        info = {}
        return state, reward, terminated, truncated, info
        


    def _start_new_round (self, starting_player_index: int):

        # Resets
        self.round_discard_pile = []
        self.last_number_of_cards_played = None
        self.last_player_who_played_index = None
        self.current_rank_to_play = "Open"

        #Define the starter player
        self.starter_player_index = starting_player_index
        self.current_player_index = starting_player_index



    def _resolve_challenge (self, current_player_index, last_player_who_played_index):
        current_player = self.players[current_player_index]
        last_player_who_played = self.players[last_player_who_played_index]
        self.pass_counter = 0

        print(f"{current_player.name} doubted!")

        next_player_index = None

        got_the_cheat = False

        for i in range(self.last_number_of_cards_played):
            current_card_to_analise = self.round_discard_pile[len(self.round_discard_pile)-i-1].value
            if current_card_to_analise != self.current_rank_to_play and current_card_to_analise != "Joker":
                got_the_cheat = True
                break

        if got_the_cheat:
            print(f"{last_player_who_played.name} bought the pile!")
            # The liar receive the pile
            for card in self.round_discard_pile:
                last_player_who_played.receive_card(card)

            # The challenger starts the next round
            self._start_new_round (current_player_index)
        else:
            print(f"{current_player.name} bought the pile!")
            # The challenger receive the pile
            for card in self.round_discard_pile:
                current_player.receive_card(card)

            # The challenged starts the next round
            self._start_new_round (last_player_who_played_index)



    def _handle_pass(self, current_player_index):
        current_player = self.players[current_player_index]
        print(f"{current_player.name} passed.")
        self.pass_counter += 1



    def _play_cards(self, current_player_index, cards_to_play, announced_rank):
        
        current_player = self.players[current_player_index]
        self.current_rank_to_play = announced_rank

        # Moving the cards to the pile
        print(f"{current_player.name} played {len(cards_to_play)} card(s), announcing '{self.current_rank_to_play}'.")
        for card in cards_to_play:
            current_player.hand.remove(card)
            self.round_discard_pile.append(card)

        # Atualize the state of the game
        self.last_player_who_played_index = current_player_index
        self.last_number_of_cards_played = len(cards_to_play)
        self.pass_counter = 0

        # Reset the starter player
        self.starter_player_index = None

        if (len(current_player.hand) == 0) :
            self._last_play_judge(current_player_index, cards_to_play)
        


    def _last_play_judge(self, current_player_index, cards_to_play) :

        current_player = self.players[current_player_index]

        was_a_lie = False

        for card in cards_to_play :
            if card.value != self.current_rank_to_play and card.value != "Joker":
                was_a_lie = True
                break

        if was_a_lie : 
            print(f"{current_player.name} was caught lying on the winning play!")

            # The liar receive all cards from pile
            for card_from_pile in self.round_discard_pile:
                current_player.receive_card(card_from_pile)

            # The next player will start the next round
            next_player = (self.current_player_index+1) % len(self.players)
            self._start_new_round(next_player)
        