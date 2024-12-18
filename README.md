# An Expectimax Agent for Exploding Kittens

## Playing a single game
To simulate a single game, run `python3 exploding_kittens.py <agent1> <agent2> [print_info]`

Valid agents are: `agent_random`, `agent_depth1`, `agent_depth2`, `agent_depth3`, `agent_1second`, and `agent_3seconds`.

`print_info` is an optional argument. Set to `True` to have the simulation print the state after each action.

## Collecting data
Run `python3 collect_data.py <agent1> <agent2> <num_trials>` to simulate `num_trials` games of `agent1` vs `agent2`. Note that The agent specified by the first argument will take the first turn in the game. This script will output game data in JSON format to the `results` directory.

The `collect_data.sh` script was used to collect all data used in the analysis of this program, which can be found in tht `results` directory.