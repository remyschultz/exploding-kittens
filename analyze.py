import os
import json
from collections import defaultdict

# Directory containing the results files
RESULTS_DIR = "results"

matchups_data = defaultdict(lambda: {
    "agent1_as_P1": {"wins": 0, "losses": 0, "total": 0},
    "agent2_as_P1": {"wins": 0, "losses": 0, "total": 0},
    "overall": {"agent1_wins": 0, "agent2_wins": 0, "total": 0}
})

for filename in os.listdir(RESULTS_DIR):
    if not filename.startswith("results-") or not filename.endswith(".json"):
        continue

    parts = filename[8:-5].split("-vs-")
    if len(parts) != 2:
        continue

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