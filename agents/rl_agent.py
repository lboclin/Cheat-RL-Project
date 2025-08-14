import torch
import torch.nn as nn
import random
import numpy as np
from .q_network import Q_Network

class RLAgent:
    """
    The main agent class that uses a multi-head Q-Network to learn and play Cheat.
    It encapsulates the network, the decision-making logic (action selection),
    and the learning process.
    """
    def __init__(self, input_size: int, epsilon: float = 1.0):
        """
        Initializes the agent.

        Args:
            input_size (int): The size of the state vector.
            epsilon (float): The initial exploration rate for the epsilon-greedy strategy.
        """
        self.epsilon = epsilon
        self.epsilon_decay = 0.9995
        self.epsilon_min = 0.01

        # Mappings for translating between network outputs and game logic
        self.card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
        self.rank_to_index = {value: i for i, value in enumerate(self.card_values)}

        # Initialize the two Q-Networks for DQN
        self.policy_net = Q_Network(input_size)
        self.target_net = Q_Network(input_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # Placeholders for optimizer and replay memory
        # self.optimizer = ...
        # self.memory = ...

    def choose_action(self, state: np.ndarray, valid_actions: dict, player_hand: list) -> tuple:
        """
        Selects an action based on the current state using an epsilon-greedy and
        hierarchical decision process.

        Args:
            state (np.ndarray): The current state vector from the environment.
            valid_actions (dict): A dictionary detailing legal actions.
            player_hand (list): The list of Card objects in the current player's hand.
        
        Returns:
            tuple: The structured action (action_type, cards_to_play, announced_rank).
        """
        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            return self._choose_random_valid_action(valid_actions, player_hand)
        
        # Exploitation path
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.policy_net(state_tensor)

            # --- HIERARCHICAL DECISION LOGIC ---
            
            # 1. Decide Action Type
            action_type_q = q_values["action_type"][0]
            masked_action_q = torch.full_like(action_type_q, -torch.inf)
            masked_action_q[valid_actions["types"]] = action_type_q[valid_actions["types"]]
            action_type = torch.argmax(masked_action_q).item()

            # Default values
            cards_to_play = []
            announced_rank = None

            if action_type == 2: # If the decision is to 'Play'
                # 2. Decide Rank and Quantity to Announce
                if valid_actions["is_starter"]:
                    rank_q = q_values["rank_claim"][0]
                    announced_rank_idx = torch.argmax(rank_q).item()
                    announced_rank = self.card_values[announced_rank_idx + 1] # +1 to skip Joker
                else:
                    announced_rank = valid_actions["current_rank"]

                quantity_q = q_values["quantity_claim"][0]
                masked_quantity_q = torch.full_like(quantity_q, -torch.inf)
                masked_quantity_q[valid_actions["quantities"]] = quantity_q[valid_actions["quantities"]]
                quantity_to_play = torch.argmax(masked_quantity_q).item() + 1
                
                # 3. Decide WHICH Cards to Play (Your New Logic)
                cards_to_play = self._select_cards_with_rank_strategy(
                    q_values["rank_selection"][0],
                    player_hand,
                    quantity_to_play
                )

            return (action_type, cards_to_play, announced_rank)

    def _select_cards_with_rank_strategy(self, rank_q_values, player_hand, quantity):
        """
        Selects the best cards from the hand to play based on rank Q-values.
        """
        # Get Q-values for the ranks of cards currently in the player's hand
        hand_ranks = {card.value for card in player_hand}
        
        # Create a list of (Q-value, rank) tuples for sorting
        rank_preferences = []
        for rank in hand_ranks:
            rank_index = self.rank_to_index[rank]
            rank_preferences.append((rank_q_values[rank_index].item(), rank))
            
        # Sort ranks by their Q-value in descending order (best ranks first)
        rank_preferences.sort(key=lambda x: x[0], reverse=True)
        
        # Build the hand to play by iterating through the sorted rank preferences
        chosen_cards = []
        for _, rank in rank_preferences:
            cards_of_rank = [card for card in player_hand if card.value == rank]
            
            # Add cards of this rank until the desired quantity is reached
            needed = quantity - len(chosen_cards)
            chosen_cards.extend(cards_of_rank[:needed])
            
            if len(chosen_cards) == quantity:
                break
        
        return chosen_cards

    def _choose_random_valid_action(self, valid_actions: dict, player_hand: list) -> tuple:
        """
        Helper function to select a completely random but valid action for exploration.
        """
        action_type = random.choice(valid_actions["types"])
        
        cards_to_play = []
        announced_rank = None

        if action_type == 2: # Play
            if valid_actions["is_starter"]:
                announced_rank = random.choice(valid_actions["ranks"])
            else:
                announced_rank = valid_actions["current_rank"]

            quantity = random.choice(valid_actions["quantities"])+1
            
            # For random play, just pick any N cards from the hand
            if len(player_hand) >= quantity:
                cards_to_play = random.sample(player_hand, k=quantity)

        return (action_type, cards_to_play, announced_rank)