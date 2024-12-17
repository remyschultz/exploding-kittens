from exploding_kittens import play_game, agent_random, agent_depth1, agent_depth2, agent_depth3, agent_1second, agent_3seconds
import sys, json
import os.path

data_dir = 'results/'

agents = {
    'agent_random': agent_random,
    'agent_depth1': agent_depth1,
    'agent_depth2': agent_depth2,
    'agent_depth3': agent_depth3,
    'agent_1second': agent_1second,
    'agent_3seconds': agent_3seconds
}

if len(sys.argv) != 4:
    print('Usage: python3 collect_data.py <agent1> <agent2> <num_trials>')
    sys.exit(1)

agent1 = sys.argv[1]
agent2 = sys.argv[2]
num_trials = int(sys.argv[3])

if agent1 not in agents:
    print('Argument agent1 is not valid')
    sys.exit(1)

if agent2 not in agents:
    print('Argument agent2 is not valid')
    sys.exit(1)

filename = f'results-{agent1}-vs-{agent2}'
n = 2
while os.path.isfile(data_dir + filename + '.json'):
    if n == 2:
        filename += '_2'
    else:
        filename = filename.rsplit('_', 1)[0] + f'_{n}'
    n += 1
filename += '.json'


results = []
for i in range(num_trials):
    try:
        result = play_game(agents[agent1], agents[agent2])
        print(f'Completed {i+1} of {num_trials} trials')
    except:
        result = {'status': 'failure'}
        print(f'Trial {i+1}: Exception')
    
    results.append(result)



with open(data_dir + filename, 'w+') as f:
    f.write(json.dumps(results))