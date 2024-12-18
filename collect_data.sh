# !/bin/bash

python3 collect_data.py agent_depth1 agent_depth2 50
python3 collect_data.py agent_depth2 agent_depth1 50

python3 collect_data.py agent_depth1 agent_random 50
python3 collect_data.py agent_random agent_depth1 50

python3 collect_data.py agent_depth2 agent_random 50
python3 collect_data.py agent_random agent_depth2 50

python3 collect_data.py agent_depth3 agent_random 25
python3 collect_data.py agent_random agent_depth3 25

python3 collect_data.py agent_1second agent_random 15
python3 collect_data.py agent_random agent_1second 15

python3 collect_data.py agent_depth1 agent_1second 25
python3 collect_data.py agent_1second agent_depth1 25

python3 collect_data.py agent_depth2 agent_1second 25
python3 collect_data.py agent_1second agent_depth2 25

python3 collect_data.py agent_depth3 agent_1second 10
python3 collect_data.py agent_1second agent_depth3 10

python3 collect_data.py agent_depth1 agent_depth1 50
python3 collect_data.py agent_depth2 agent_depth2 50

python3 collect_data.py agent_random agent_random 100
python3 collect_data.py agent_1second agent_1second 10

python3 collect_data.py agent_depth3 agent_depth2 10
python3 collect_data.py agent_depth2 agent_depth3 10

python3 collect_data.py agent_depth3 agent_depth1 10
python3 collect_data.py agent_depth1 agent_depth3 10

python3 collect_data.py agent_depth3 agent_depth3 5
