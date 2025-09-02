import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import numpy as np
from .q_network import Q_Network
from .replay_memory import ReplayMemory, Transition

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

        # --- DQN ARCHITECTURE ---
        self.policy_net = Q_Network(input_size)
        self.target_net = Q_Network(input_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # --- LEARNING COMPONENTS ---
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.0001)
        self.memory = ReplayMemory(10000)

    def choose_action(self, state: np.ndarray, valid_actions: dict) -> tuple:
        """
        Selects an action based on the current state using an epsilon-greedy and
        hierarchical decision process.

        Args:
            state (np.ndarray): The current state vector from the environment.
            valid_actions (dict): A dictionary detailing legal actions.
        
        Returns:
            tuple: The structured action (action_type, cards_to_play, announced_rank).
        """
        player_hand = valid_actions["player_hand"]

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
    
    def learn(self, batch_size: int):
        """
        Performs one step of the optimization process. It samples a batch from
        memory and uses it to update the policy network's weights based on the
        multi-head outputs.
        """
        if len(self.memory) < batch_size:
            return

        # 1. SAMPLE BATCH
        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))

        # 2. CONVERT TO TENSORS
        state_batch = torch.tensor(np.array(batch.state), dtype=torch.float32)
        next_state_batch = torch.tensor(np.array(batch.next_state), dtype=torch.float32)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float32)
        done_batch = torch.tensor(batch.done, dtype=torch.bool)

        # --- 3. UNPACK THE COMPLEX ACTION BATCH ---
        # Unpack all components of the action tuple for the entire batch
        action_types = torch.tensor([a[0] for a in batch.action], dtype=torch.int64).view(-1, 1)
        
        # For play-specific actions, we use a placeholder (-1) if the action was not 'play'
        # Note: announced_rank for non-starters is fixed, so we primarily learn the starter's choice
        announced_ranks_idx = []
        quantities_idx = []
        for action_tuple in batch.action:
            action_type, cards, rank = action_tuple
            if action_type == 2: # Is a 'play' action
                # Convert rank name to index. We assume Joker (index 0) is not a valid claim.
                # The network outputs 13 ranks (Ace-King), so we map them to 0-12.
                # self.rank_to_index['Ace'] is 1, so we subtract 1.
                announced_ranks_idx.append(self.rank_to_index.get(rank, 1) - 1)
                
                # Quantity is 1-6, network output is 0-5. So we subtract 1.
                quantities_idx.append(len(cards) - 1 if cards else 0)
            else:
                announced_ranks_idx.append(-1) # Placeholder
                quantities_idx.append(-1)    # Placeholder

        announced_ranks_idx = torch.tensor(announced_ranks_idx, dtype=torch.int64).view(-1, 1)
        quantities_idx = torch.tensor(quantities_idx, dtype=torch.int64).view(-1, 1)

        # --- 4. CALCULATE TD TARGET (Same as before) ---
        with torch.no_grad():
            next_q_values_dict = self.target_net(next_state_batch)
            max_next_q_values = next_q_values_dict["action_type"].max(1)[0]
            target_q_values = reward_batch + (0.99 * max_next_q_values * ~done_batch) # Assuming gamma=0.99

        # --- 5. CALCULATE HIERARCHICAL LOSS ---
        
        # Get all Q-value predictions from the policy network
        q_values_dict = self.policy_net(state_batch)
        
        # a) Loss for Action Type (always calculated)
        predicted_q_for_action_type = q_values_dict["action_type"].gather(1, action_types)
        total_loss = F.smooth_l1_loss(predicted_q_for_action_type, target_q_values.unsqueeze(1))

        # b) Create a mask for 'play' actions
        play_mask = (action_types == 2).squeeze()
        
        # c) Add loss for other heads only for 'play' actions
        if play_mask.sum() > 0:
            # Loss for Rank Claim
            predicted_q_rank = q_values_dict["rank_claim"][play_mask].gather(1, announced_ranks_idx[play_mask])
            total_loss += F.smooth_l1_loss(predicted_q_rank, target_q_values[play_mask].unsqueeze(1))
            
            # Loss for Quantity Claim
            predicted_q_qty = q_values_dict["quantity_claim"][play_mask].gather(1, quantities_idx[play_mask])
            total_loss += F.smooth_l1_loss(predicted_q_qty, target_q_values[play_mask].unsqueeze(1))
            
            # (Opcional/Avançado) Loss for Rank Selection
            # Esta cabeça é mais complexa. Uma abordagem é usar MSE loss para incentivar
            # Q-values mais altos para os ranks das cartas que foram realmente jogadas.
            # Por simplicidade, vamos manter a loss principal por enquanto.

        # --- 6. BACKPROPAGATION ---
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        