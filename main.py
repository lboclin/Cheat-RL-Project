import random
import torch
import os
from cheat_env.environment import CheatEnviroment
from agents.bots import bot_strategy_80_20, bot_strategy_one_third, bot_100_0, bot_strategy_60_40
from agents.rl_agent import RLAgent

def main():
    """
    Main function to run a game of "Cheat" with 2 bots and the agent.
    """

    winners_vector = [0, 0, 0]

    # --- 1. GAME SETUP ---
    # Define the players, the maximum number of turns and initialize the enviroment
    player_names = ["RL_Agent", "Bot_1", "Bot_2"]
    max_turns = 250
    env = CheatEnviroment(players_names=player_names, max_episode_steps=max_turns)

    # Bot strategies
    bot_pool = [bot_strategy_60_40, bot_100_0, bot_strategy_80_20, bot_strategy_one_third]

    # Define training parameters
    num_episodes = 1
    BATCH_SIZE = 128

    # Initialize the agent
    state_size = len(env.reset())
    agent = RLAgent(input_size=state_size)

    # Load the agent's weights
    CHECKPOINT_PATH = "training_checkpoint.pth"
    if os.path.exists(CHECKPOINT_PATH):
        checkpoint = torch.load(CHECKPOINT_PATH)
        agent.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        agent.target_net.load_state_dict(checkpoint['policy_net_state_dict'])
        agent.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        agent.epsilon = checkpoint['epsilon']
        start_episode = checkpoint['episode'] + 1
        print(f"Checkpoint loaded. Resuming episode {start_episode} with epsilon={agent.epsilon:.4f}")
    else:
        print("No checkpoint found. Starting training from scratch.")

    # Define card values map for printing
    card_values = ["Joker", "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
    value_to_index = {value: i for i, value in enumerate(card_values)}

    for episode in range(num_episodes):
        
        print(f"--- Episode {episode+1} ---")

        # --- 2. GAME START (EPISODE) ---
        state = env.reset()
        terminated = False
        truncated = False

        # Define bot strategies
        opponent_1_strategy = random.choice(bot_pool)
        opponent_2_strategy = random.choice(bot_pool)

        # --- 3. THE MAIN GAME LOOP ---
        while not terminated and not truncated:
            current_player = env.players[env.current_player_index]
            state = env._get_state()

            
            # --- Print the current state for visualization ---
            print("-" * 30)
            print(f"Turn: {env.turn_count} | Player's Turn: {current_player.name}")
            
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
            if current_player.name == "RL_Agent":
                action = agent.choose_action(env._get_state(), env.get_valid_actions())

            elif current_player.name == "Bot_1":
                action = opponent_1_strategy(current_player, env.current_rank_to_play)

            elif current_player.name == "Bot_2":
                action = opponent_2_strategy(current_player, env.current_rank_to_play)

            action_type, cards, rank = action
            print(f"Action chosen by {current_player.name}: Type={action_type}, Cards={cards}, Rank='{rank}'")

            next_state, reward, terminated, truncated, info = env.step(action)

            # --- AGENT LEARNING PROCESS --- 

            if current_player.name == "RL_Agent":
                done = terminated or truncated # Define if the episode has finished
                agent.memory.push(state, action, next_state, reward, done) # Atualize the memory
                agent.learn(BATCH_SIZE) # Call learn funciton


        # Print the end of an episode
        print("\n" + "=" * 30)
        if terminated:
            if env.winner.name == "RL_Agent":
                winners_vector[0] += 1
            elif env.winner.name == "Bot_1":
                winners_vector[1] += 1
            else:
                winners_vector[2] += 1
            
            print(f"GAME OVER! The winner is: {env.winner.name}")
        elif truncated:
            print(f"GAME OVER! Reached the limit of {max_turns} turns.")
        print("=" * 30)
        print("\n")
        
        # Save the model each 100 episodes
        if episode % 100 == 0:
            checkpoint = {
                'episode': episode,
                'policy_net_state_dict': agent.policy_net.state_dict(),
                'optimizer_state_dict': agent.optimizer.state_dict(),
                'epsilon': agent.epsilon
            }
            torch.save(checkpoint, CHECKPOINT_PATH)
            print(f"Checkpoint saved in episode {episode+1}")

    # Save the model for the last time
    torch.save(checkpoint, CHECKPOINT_PATH)
    print("Training finished. Checkpoint saved.")

    print(winners_vector)


if __name__ == "__main__":
    main()