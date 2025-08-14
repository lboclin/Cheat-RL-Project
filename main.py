import random
from cheat_env.environment import CheatEnviroment
from agents.bots import bot_strategy_80_20, bot_strategy_one_third
from agents.rl_agent import RLAgent

def main():
    """
    Main function to run a game of "Cheat" with three bots,
    each using the bot_strategy_80_20 logic.
    """
    # --- 1. GAME SETUP ---
    # Create the game with 3 bot players.
    player_names = ["RL_Agent", "Bot_103", "Bot_8020"]
    env = CheatEnviroment(players_names=player_names)

    # Initialize the agent
    state_size = len(env.reset())
    agent = RLAgent(input_size=state_size)

    # --- 2. GAME START (EPISODE) ---
    state = env.reset()
    terminated = False
    turn_count = 1
    max_turns = 250 # A safety limit to prevent infinite loops during testing

    # --- Define card values map for printing ---
    card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
    value_to_index = {value: i for i, value in enumerate(card_values)}


    # --- 3. THE MAIN GAME LOOP ---
    while not terminated and turn_count < max_turns:
        
        current_player_index = env.current_player_index
        current_player = env.players[current_player_index]
        
        # --- Print the current state for visualization ---
        print("-" * 30)
        print(f"Turn: {turn_count} | Player's Turn: {current_player.name}")
        
        for p in env.players:
            # Create a frequency vector for the player's hand
            hand_vector = [0] * 14
            for card in p.hand:
                if card.value in value_to_index:
                    hand_vector[value_to_index[card.value]] += 1
            
            print(f"  - {p.name}: {len(p.hand)} cards -> Frequencies: {hand_vector}")


        print(f"Rank to Play: '{env.current_rank_to_play}' | Cards in Pile: {len(env.round_discard_pile)}")
        
        # --- ACTION DECISION ---
        action = None
        if current_player is env.rl_agent:
            valid_actions = env.get_valid_actions()
            action = agent.choose_action(state, valid_actions, current_player.hand)
        else:
            if current_player.name == "Bot_8020":
                action = bot_strategy_80_20(current_player, env.current_rank_to_play)
            else:
                action = bot_strategy_one_third(current_player, env.current_rank_to_play)
        
        action_type, cards, rank = action
        print(f"Action chosen by {current_player.name}: Type={action_type}, Cards={cards}, Rank='{rank}'")

        # --- ENVIRONMENT PROCESSES THE ACTION ---
        # The chosen action is passed to the step function.
        state, reward, terminated, truncated, info = env.step(action)

        turn_count += 1

    # --- 4. END OF GAME ---
    print("\n" + "=" * 30)
    if terminated:
        print(f"GAME OVER! The winner is: {env.winner.name}")
    else:
        print(f"GAME OVER! Reached the limit of {max_turns} turns.")
    print("=" * 30)


if __name__ == "__main__":
    main()