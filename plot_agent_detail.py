import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def plot_detailed_agent_performance(
    file_path='win_rate_log.csv',
    max_episodes_focus=20000,
    epsilon_decay=0.999985,
    epsilon_min=0.01,
    avg_turns_per_episode=34,
    log_interval=500
):
    """
    Creates a detailed plot focusing on the RL Agent's win rate evolution
    over a specified range of episodes, with intelligent epsilon annotations.
    """
    try:
        df_full = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    # --- 1. Prepare Data ---
    df = df_full[df_full['Episode'] <= max_episodes_focus].copy()

    # --- 2. Calculate Extra Metrics for Annotations ---
    def calculate_epsilon(episode):
        steps = episode * avg_turns_per_episode
        epsilon = max(epsilon_min, 1.0 * (epsilon_decay ** steps))
        return epsilon

    df_full['RL_Agent_Wins'] = (df_full['RL_Agent'] / 100) * log_interval
    total_wins_at_focus = int(df_full[df_full['Episode'] <= max_episodes_focus]['RL_Agent_Wins'].sum())
    total_wins_overall = int(df_full['RL_Agent_Wins'].sum())
    max_episodes_total = df_full['Episode'].max()

    # --- 3. Create the Plot ---
    fig, ax = plt.subplots(figsize=(15, 8))
    
    ax.plot(df['Episode'], df['RL_Agent'], marker='o', linestyle='-', label='RL Agent Win Rate', color='royalblue', zorder=2)

    # --- 4. Add Epsilon Annotations ---
    for index, row in df.iterrows():
        episode = int(row['Episode'])
        win_rate = row['RL_Agent']
        epsilon_val = calculate_epsilon(episode)
        
        # CHANGED: Only add the annotation if epsilon is still decaying (greater than the minimum).
        if epsilon_val > epsilon_min:
            ax.annotate(f'ε={epsilon_val:.2f}',
                        xy=(episode, win_rate),
                        xytext=(0, 15),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=9,
                        arrowprops=dict(arrowstyle="->", color='gray'))

    # --- 5. Add Total Wins Text Box ---
    stats_text = (f"Total Wins (in {max_episodes_focus/1000:.0f}k episodes): {total_wins_at_focus}\n"
                  f"Total Wins (in {max_episodes_total/1000:.0f}k episodes): {total_wins_overall}")
                  
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='left', bbox=props)

    # --- 6. Customize the Plot ---
    ax.set_title(f'Detailed Analysis of RL Agent Win Rate (First {max_episodes_focus/1000:.0f}k Episodes)', fontsize=16)
    ax.set_xlabel('Episodes', fontsize=12)
    ax.set_ylabel('Interval Win Rate (%)', fontsize=12)
    
    ax.set_ylim(0, 30) 
    
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x/1000)}k' if x > 0 else 0))

    ax.legend(loc='lower right')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # --- 7. Save and Show ---
    output_filename = 'rl_agent_performance_zoom.png'
    plt.savefig(output_filename, dpi=300)
    print(f"Graphic saved as '{output_filename}'")
    
    plt.show()

if __name__ == '__main__':
    plot_detailed_agent_performance(file_path='win_rate_log.csv')