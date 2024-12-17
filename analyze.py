import os
import json
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

# Directory containing the results files
RESULTS_DIR = "results"

matchups_data = defaultdict(lambda: {
    "agent1_as_P1": {"wins": 0, "losses": 0, "total": 0},
    "agent2_as_P1": {"wins": 0, "losses": 0, "total": 0},
    "overall": {"agent1_wins": 0, "agent2_wins": 0, "total": 0}
})

timing_data = defaultdict(lambda: [])

for filename in os.listdir(RESULTS_DIR):
    if not filename.startswith("results-") or not filename.endswith(".json"):
        continue

    parts = filename[8:-5].split("-vs-")
    if len(parts) != 2:
        continue

    p1_agent, p2_agent = parts
    agent1, agent2 = sorted(parts)

    p1 = 'agent1' if filename.index(agent1) <= filename.index(agent2) else 'agent2'
    p2 = 'agent2' if filename.index(agent1) <= filename.index(agent2) else 'agent1'

    matchup_key = f"{agent1} vs {agent2}"
    filepath = os.path.join(RESULTS_DIR, filename)

    # Read the file content
    with open(filepath, "r") as file:
        games = json.load(file)

    for game in games:
        winner = game["winner"]

        if winner == "P1":
            matchups_data[matchup_key][f"{p1}_as_P1"]["wins"] += 1
            matchups_data[matchup_key]["overall"][f"{p1}_wins"] += 1
        else:
            matchups_data[matchup_key][f"{p1}_as_P1"]["losses"] += 1
            matchups_data[matchup_key]["overall"][f"{p2}_wins"] += 1
        
        matchups_data[matchup_key][f"{p1}_as_P1"]["total"] += 1
        matchups_data[matchup_key]["overall"]["total"] += 1

        timing_data[p1_agent] += game['p1_time']
        timing_data[p2_agent] += game['p2_time']


print('Matchup analysis...')
for matchup, data in matchups_data.items():
    agent1, agent2 = matchup.split(" vs ")

    try:

        print(matchup)
        print(f"\t{agent1} starts: {data['agent1_as_P1']['wins']} W / {data['agent1_as_P1']['losses']} L ({data['agent1_as_P1']['total']} Total) - {data['agent1_as_P1']['wins'] / data['agent1_as_P1']['total'] * 1000 // 10}%")
        print(f"\t{agent2} starts: {data['agent2_as_P1']['wins']} W / {data['agent2_as_P1']['losses']} L ({data['agent2_as_P1']['total']} Total) - {data['agent2_as_P1']['wins'] / data['agent2_as_P1']['total'] * 1000 // 10}%")
        print(f"\tOverall: {agent1} {data['overall']['agent1_wins']} ({data['overall']['agent1_wins'] / data['overall']['total'] * 1000 // 10}%) / {agent2} {data['overall']['agent2_wins']} ({data['overall']['agent2_wins'] / data['overall']['total'] * 1000 // 10}%)")
        print()
    except:
        continue

print('\nTiming analyis...')
for agent, data in timing_data.items():
    title=f"Frequency Distribution for {agent} (n={len(data)})"

    if not isinstance(data, (list, np.ndarray)) or len(data) == 0:
        raise ValueError("Input data must be a non-empty list or numpy array of floats.")

    data = np.array(data)

    mean = np.mean(data)
    median = np.median(data)

    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=20, color='skyblue', edgecolor='black')
    plt.axvline(mean, color='red', linestyle='dashed', linewidth=1, label=f"Mean: {mean:.2f}")
    plt.axvline(median, color='green', linestyle='dotted', linewidth=1, label=f"Median: {median:.2f}")

    plt.title(title)
    plt.xlabel("Time to choose move (sec)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

