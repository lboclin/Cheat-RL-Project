import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def plot_win_rate_log(file_path='win_rate_log.csv'):
    """
    Reads the win rate log CSV file and plots the evolution of win rates for
    each player/strategy over the course of the training episodes.

    Args:
        file_path (str): The path to the win_rate_log.csv file.
    """
    try:
        # --- 1. Load the Data ---
        # Reads the CSV file. The data should be in percentage format.
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please run the training script first to generate the log file.")
        return

    if df.empty:
        print(f"The file '{file_path}' is empty. No data to plot.")
        return

    # --- 2. Setup the Plot ---
    fig, ax = plt.subplots(figsize=(14, 8))
    player_columns = df.columns.drop('Episode')

    # --- 3. Plot Each Player's Win Rate History ---
    for player in player_columns:
        ax.plot(df['Episode'], df[player], marker='o', linestyle='-', label=player)

    # --- 4. Customize the Chart for Percentage Data ---
    ax.set_title('Evolution of Win Rate (%) During Training', fontsize=16)
    ax.set_xlabel('Episodes', fontsize=12)
    ax.set_ylabel('Halftime win rate', fontsize=12)
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x/1000)}k' if x > 0 else 0))
    
    ax.legend(title='Players', loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()

    # --- 5. Save and Show the Plot ---
    output_filename = 'win_rate_evolution.png'
    plt.savefig(output_filename, dpi=300)
    print(f"Graphic saved as '{output_filename}'")

    plt.show()


if __name__ == '__main__':
    plot_win_rate_log()