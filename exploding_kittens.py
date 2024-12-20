import random, math, time
from copy import deepcopy
from itertools import permutations
import sys

UNKNOWN = 0
DEFUSE = 1
EK = 2
BCAT = 3
WCAT = 4
HCAT = 5
RCAT = 6
TCAT = 7
ATTACK = 8
FAVOR = 9
NOPE = 10
FUTURE = 11
SHUFFLE = 12
SKIP = 13


cards = ['UNKNOWN', 'DEFUSE', 'EK', 'BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP']
# default_counts = [0,       4,    1,      4,      4,      4,      4,      4,        2,      4,       5,        5,         4,      4]
counts = [       0,        4,    1,      4,      4,      4,      4,      4,        2,      4,       0,        5,         4,      4]
start_hand_size = 8

FULL_DECK = lambda: deepcopy(counts)

class State:
    def __init__(self, player='MAX'):
        self.deal_cards()

        self.known_max = [start_hand_size - 1, 1] + ([0] * 12)
        self.known_min = [start_hand_size - 1, 1] + ([0] * 12)

        self.max_known_deck = []
        self.min_known_deck = []

        self.attack = False
        self.future = False
        self.cat_card = False
        self.favor = False
        self.drawing = None
        self.replace_ek = False

        self.to_move = player
        self.action_history = []

        self.perspective = 'TRUTH'

    # Min should perceive themselves as Max
    def percept(self):
        state = deepcopy(self)
        if self.to_move == 'MAX':
            state.deck = [state.deck[i] if i in state.max_known_deck else UNKNOWN for i in range(len(state.deck))]
            add_to_pool = State.subtract_cards(state.min_hand, state.known_min)
            add_to_pool[UNKNOWN] = 0
            state.pool = State.add_cards(state.pool, add_to_pool)
            state.min_hand = deepcopy(self.known_min)

            state.perspective = 'MAX'
            
        else:
            state.deck = [UNKNOWN if i not in self.min_known_deck else self.deck[i] for i in range(len(self.deck))]
            add_to_pool = State.subtract_cards(state.max_hand, state.known_max)
            add_to_pool[UNKNOWN] = 0
            state.pool = State.add_cards(state.pool, add_to_pool)
            state.max_hand = deepcopy(self.known_max)

            state.perspective = 'MIN'

        return state

    def get_deck(self, player=None):
        if player == None:
            if self.to_move == 'CHANCE':
                player = self.drawing
            else:
                player = self.to_move
        if player == 'MAX':
            known = self.max_known_deck
        else:
            known = self.min_known_deck
        return [c if i in known else UNKNOWN for i, c in enumerate(self.deck)]

    def deal_cards(self):
        deck = FULL_DECK()
        deck[EK] = 0
        deck[DEFUSE] = 0

        self.deck = []
        for card, count in enumerate(deck):
            self.deck += [card] * count
        random.shuffle(self.deck)

        self.max_hand = [0] * len(counts)
        self.min_hand = [0] * len(counts)

        for card in self.deck[0 : start_hand_size - 1]:
            self.max_hand[card] += 1
        self.max_hand[DEFUSE] = 1

        for card in self.deck[start_hand_size - 1 : 2 * start_hand_size - 2]:
            self.min_hand[card] += 1
        self.min_hand[DEFUSE] = 1

        self.deck = self.deck[2 * start_hand_size - 2 :] + [EK] * counts[EK] + [DEFUSE] * (counts[DEFUSE] - 2)
        random.shuffle(self.deck)

        self.pool = State.subtract_cards(FULL_DECK(), self.max_hand, self.min_hand)

    def deal_hand(self):
        hand = [0] * 14
        hand[DEFUSE] = 1
        self.pool[DEFUSE] -= 1

        for _ in range(start_hand_size - 1):
            card = random.choice([i for i in range(len(self.pool)) if i > EK and self.pool[i] > 0])
            hand[card] += 1
            self.pool[card] -= 1

        return hand

    def get_current_hand(self, player=None):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            return self.max_hand
        return self.min_hand

    def add_to_hand(self, card, player=None, count=1, known=False):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            self.max_hand[card] += count
            if known:
                self.known_max[card] += count
            else:
                self.known_max[UNKNOWN] += count
        else:
            self.min_hand[card] += count
            if known:
                self.known_min[card] += count
            else:
                self.known_min[UNKNOWN] += count

    def remove_from_hand(self, card, player=None, count=1):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            self.max_hand[card] -= count
            if self.known_max[card] == 0:
                self.known_max[UNKNOWN] -= count
            else:
                self.known_max[card] -= count
        else:
            self.min_hand[card] -= count
            if self.known_min[card] == 0:
                self.known_min[UNKNOWN] -= count
            else:
                self.known_min[card] -= count

    def opposite_player(self, player=None):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            return 'MIN'
        return 'MAX'

    def print(self):
        print('--------STATE--------')
        print(f"{self.to_move}'s turn")
        print("Max's Hand:")
        for card in cards:
            if self.max_hand[cards.index(card)] != 0:
                print(f"\t{card}: {self.max_hand[cards.index(card)]}")

        print("Known Max:")
        for card in cards:
            if self.known_max[cards.index(card)] != 0:
                print(f"\t{card}: {self.known_max[cards.index(card)]}")
        
        print("Min's Hand:")
        for card in cards:
            if self.min_hand[cards.index(card)] != 0:
                print(f"\t{card}: {self.min_hand[cards.index(card)]}")

        print("Known Min:")
        for card in cards:
            if self.known_min[cards.index(card)] != 0:
                print(f"\t{card}: {self.known_min[cards.index(card)]}")
        
        print("Pool:")
        for card in cards:
            if self.pool[cards.index(card)] != 0:
                print(f"\t{card}: {self.pool[cards.index(card)]}")
        
        print("Deck:")
        print([cards[c] for c in self.deck])

        print(f"Deck size: {len(self.deck)}")

        print(f"action_history: {self.action_history}")

        print('---------------------\n')
        

    def subtract_cards(a, *b):
        r = deepcopy(a)
        for bb in b:
            for i in range(1, len(r)):
                r[i] -= bb[i]
        return r

    def add_cards(a, *b):
        r = deepcopy(a)
        for bb in b:
            for i in range(1, len(r)):
                r[i] += bb[i]
        return r

# returns a list of probabilities for each action
def probablity(state, actions):
    ps = [0] * len(actions)

    if len(actions) == 1:
        return [1]

    for i, a in enumerate(actions):
        if a.startswith('DEFUSE_'):
            ps[i] = 1
            continue

        if a.startswith('FAVOR_'):
            a = a.split('_', 1)[1]

        if a.startswith('DRAW_'):
            card = cards.index(a.split('_', 1)[1])
            ps[i] = state.pool[card] / sum(state.pool)
        
        if a == 'DRAW':
            ps[i] = 1

        if a.startswith('FUTURE_'):
            cs = [cards.index(c) for c in a.split('_')[1:]]
            ps[i] = 1

            pool = deepcopy(state.pool)
            
            for c in cs:
                K = pool[c]                 # number of desired type
                N = sum(pool)               # population size

                ps[i] *= K/N

                pool[c] -= 1

        if a.startswith('CAT_'):
            c = cards.index(a.split('_', 1)[1])
            hand = state.get_current_hand(player=state.opposite_player(player=state.drawing))
            if hand[c] > 0:
                ps[i] = 1
            else:
                ps[i] = state.pool[c] / sum(state.pool)
        
        if a in cards:
            if state.get_current_hand()[cards.index(a)] > 0:
                # Player definitely has the card
                ps[i] = 1
            else:
                # Calculate likelyhood of player having the card
                # Use cumulative hypergeometric distribution
                K = state.pool[cards.index(a)]                  # number of desired type
                N = sum(state.pool)                             # population size
                n = min(N, state.get_current_hand()[UNKNOWN])   # number of draws
                needed_successes = 1                            # number of needed successes

                for k in range(needed_successes, min(N, n) + 1):
                    ps[i] += math.comb(K, k) * math.comb(N - K, n - k) / math.comb(N, n)

    return ps



def actions(state):
    adjusted_pool = deepcopy(state.pool)
    for card in state.get_deck():
        if card != UNKNOWN:
            adjusted_pool[card] -= 1

    # Chance node - return all drawable cards
    if state.to_move == 'CHANCE':
        if state.future:
            top = state.get_deck()[-3:][::-1]
            known = sum([1 for c in top if c != UNKNOWN])
            remaining = min(3 - known, len(state.deck))

            if remaining == 0:
                return [f"FUTURE_{'_'.join([cards[c] for c in top])}"]
            
            pool = [i for i, c in enumerate(state.pool) if c > 0]
            perms = permutations(list(set(pool)), r=remaining)
            actions = []
            
            for perm in perms:
                i = 0
                cs = []
                for c in top:
                    if c == UNKNOWN:
                        cs.append(perm[i])
                        i += 1
                    else:
                        cs.append(c)
                actions.append(f"FUTURE_{'_'.join([cards[c] for c in cs])}")

            # if known == 1:
            #     print(actions)
            #     print(top)
            #     print(state.deck)
            #     input()
            return actions

        elif state.cat_card:
            hand = state.get_current_hand(player=state.opposite_player(player=state.drawing))
            candidates = State.add_cards(hand, adjusted_pool)
            candidates[UNKNOWN] = 0
            return [f"CAT_{cards[i]}" for i, c in enumerate(candidates) if c > 0]

        elif state.replace_ek:
            return [f'DEFUSE_{pos}' for pos in range(len(state.deck)+1)]

        else:
            card = state.get_deck()[-1]

            if card != UNKNOWN:
                return [f'DRAW_{cards[card]}']

            if sum(state.pool) == state.max_hand[UNKNOWN] + state.min_hand[UNKNOWN] + 1:
                # Only the EK remains in the actual deck
                return ['DRAW_EK']

            
            return [f'DRAW_{cards[card]}' for card, count in enumerate(adjusted_pool) if count > 0]
        

    hand = deepcopy(state.get_current_hand())
    
    # This is to determine what actions the player could possibly take, given that their opponent may not know exactly what cards they have
    for card, count in enumerate(adjusted_pool):
        if card != EK:
            hand[card] += min(count, hand[UNKNOWN])
    hand[UNKNOWN] = 0

    actions = []
    if state.favor:
        for card, count in enumerate(hand):
            if count > 0:
                actions.append(f"FAVOR_{cards[card]}")
        return actions

    # Player drew EK - do they have Defuse?
    if hand[EK] == 1:
        if hand[DEFUSE] > 0 or (hand[UNKNOWN] > 0 and adjusted_pool[DEFUSE] > 0):
            # return [f'DEFUSE_{pos}' for pos in range(len(state.deck)+1)]
            return ['DEFUSE']
        else:
            return []

    # Normal turn - can draw a card or play a card
    actions = []
    if len(state.deck) > 0:
        actions.append('DRAW')
    for card, count in enumerate(hand):
        if card <= DEFUSE:
            # Defuse or EK - ignore
            continue
        elif card <= TCAT:
            # Cat cards - need 2
            if count >= 2 and sum(state.get_current_hand(player=state.opposite_player())) > 0:
                actions.append(cards[card])
        elif card == ATTACK:
            # no stacking attacks
            if count >= 1 and not state.attack:
                actions.append('ATTACK')
        elif card == FAVOR:
            if count >= 1 and sum(state.get_current_hand(player=state.opposite_player())) > 0:
                actions.append('FAVOR')
        elif card == FUTURE:
            if count >= 1 and len(state.deck) > 1:
                actions.append('FUTURE')
        else:
            # All other cards
            if count >= 1:
                actions.append(cards[card])

    return actions

def result(state, action):
    if action == None:
        return state
    
    result_state = deepcopy(state)

    result_state.action_history = [f"{state.to_move}: {action}"] + state.action_history

    if action == 'DRAW':
        result_state.drawing = state.to_move
        result_state.to_move = 'CHANCE'
        return result_state

    elif action.startswith('DRAW_'):

        result_state.deck.pop()

        # if c != 0 and c != cards.index(action.split('_', 1)[1]):
        #     print(c, cards.index(action.split('_', 1)[1]))
        #     input()


        result_state.max_known_deck = [i for i in state.max_known_deck if i < len(result_state.deck)]
        result_state.min_known_deck = [i for i in state.min_known_deck if i < len(result_state.deck)]

        result_state.to_move = state.drawing
        result_state.drawing = None

        # result_state.max_known_top = state.max_known_top[1:]
        # result_state.min_known_top = state.min_known_top[1:]

        # result_state.max_known_ek -= 1
        # result_state.min_known_ek -= 1


        card = cards.index(action.split('_', 1)[1])

        result_state.add_to_hand(card, known=(card==EK))
        result_state.pool[card] -= 1

        if card == EK:
            result_state.attack = False
            return result_state


        if state.attack:
            result_state.attack = False
        else:
            result_state.to_move = result_state.opposite_player()

        return result_state

    elif action.startswith('DEFUSE_'):
        pos = int(action.split('_', 1)[1])

        result_state.to_move = state.drawing
        result_state.drawing = None
        result_state.remove_from_hand(DEFUSE, player=result_state.opposite_player())
        result_state.remove_from_hand(EK, player=result_state.opposite_player())
        result_state.pool[EK] += 1 # Put the EK back in the pool

        # Put EK into deck at pos
        result_state.deck.insert(pos, EK)

        # Reset known deck info
        result_state.max_known_deck = []
        result_state.min_known_deck = []

        result_state.replace_ek = False

        return result_state

    elif action.startswith('FAVOR_'):
        card = cards.index(action.split('_', 1)[1])
        
        result_state.remove_from_hand(card)
        result_state.add_to_hand(card, player=state.opposite_player(), known=True)
        
        result_state.favor = False

        result_state.to_move = state.opposite_player()

        return result_state

    elif action.startswith('FUTURE_'):
        # not always 3 cards
        future_cards = [cards.index(c) for c in action.split('_')[1:]]
        result_state.to_move = state.drawing
        result_state.drawing = False
        result_state.future = False

        for i, fc in enumerate(future_cards):
            result_state.deck[-(i + 1)] = fc

            if result_state.to_move == 'MAX':
                result_state.max_known_deck.append(len(state.deck) - (i+1))

            if result_state.to_move == 'MIN':
                result_state.min_known_deck.append(len(state.deck) - (i+1))

        return result_state
    
    elif action.startswith('CAT_'):
        card = cards.index(action.split('_', 1)[1])
        result_state.to_move = state.drawing
        result_state.drawing = False
        result_state.cat_card = False

        result_state.add_to_hand(card)
        result_state.remove_from_hand(card, player=state.opposite_player())

        return result_state


    card = cards.index(action)

    if action in ['BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT']:
        result_state.remove_from_hand(card, count=2)
        result_state.cat_card = True
        result_state.to_move = 'CHANCE'
        result_state.drawing = state.to_move
        return result_state

    if action == 'DEFUSE':
        result_state.drawing = state.opposite_player()
        result_state.to_move = 'CHANCE'
        result_state.replace_ek = True

        return result_state
    

    # Might have played a card we didn't know they had
    if state.get_current_hand()[card] == 0:
        result_state.remove_from_hand(UNKNOWN)
        # If a player plays a card that they don't for sure have, it must get removed from the pool
        result_state.pool[card] -= 1
    else:
        result_state.remove_from_hand(card)

        
    if action == 'ATTACK':
        result_state.to_move = state.opposite_player()
        result_state.attack = True

    elif action == 'SKIP':
        if not state.attack:
            result_state.to_move = state.opposite_player()
        else:
            result_state.attack = False

    elif action == 'SHUFFLE':
        if state.perspective == 'TRUTH':
            random.shuffle(result_state.deck)
        else:
            result_state.deck = [UNKNOWN] * len(state.deck)

        result_state.max_known_deck = []
        result_state.min_known_deck = []

    elif action == 'FAVOR':
        result_state.to_move = state.opposite_player()
        result_state.favor = True

    elif action == 'FUTURE':
        result_state.drawing = state.to_move
        result_state.to_move = 'CHANCE'
        result_state.future = True
       
    return result_state


def is_terminal(state):
    return state.max_hand[EK] == 1 and state.max_hand[DEFUSE] == 0 and (state.max_hand[UNKNOWN] == 0 or state.pool[DEFUSE] == 0) \
        or state.min_hand[EK] == 1 and state.min_hand[DEFUSE] == 0 and (state.min_hand[UNKNOWN] == 0 or state.pool[DEFUSE] == 0) 

def utility(state):
    if state.max_hand[DEFUSE] == 0 and state.max_hand[EK] == 1:
        return -1000
    if state.min_hand[DEFUSE] == 0 and state.min_hand[EK] == 1:
        return 1000
    return 0 # should never occur

def state_eval(state):
    score = 0


    score += 2 * (state.max_hand[SKIP] - state.min_hand[SKIP])
    score += 4 * (state.max_hand[ATTACK] - state.min_hand[ATTACK])
    score += 8 * (state.max_hand[DEFUSE] - state.min_hand[DEFUSE])
    
    score += 4 * (state.max_hand[FUTURE] - state.min_hand[FUTURE])
    score += 2 * (state.max_hand[SHUFFLE] - state.min_hand[SHUFFLE])
    score += 3 * (state.max_hand[FAVOR] - state.min_hand[FAVOR])

    score += 1 * (sum(state.max_hand[BCAT:TCAT+1]) - sum(state.min_hand[BCAT:TCAT+1]))

    score += 3 * (state.max_hand[UNKNOWN] - state.min_hand[UNKNOWN])

    score += -8 * (state.max_hand[EK] - state.min_hand[EK])

    return score

def expectimax(state, depth, cutoff_time, eval_fn):
    if depth == 0 or time.time() > cutoff_time:
        return eval_fn(state)
    if time.time() > cutoff_time:
        return eval_fn(state)
    if is_terminal(state):
        return utility(state)

    ac = actions(state)
    scores = [expectimax(result(state, a), depth - 1, cutoff_time, eval_fn) for a in ac]
    pr = probablity(state, ac)

    if len(scores) == 0:
        # state.print()
        # input()
        return eval_fn(state)

    if state.to_move == 'MAX':
        # In this case, probability means the chance that Min is *able* to take an action
        index_max = max(range(len(scores)), key=scores.__getitem__)

        # If the best move for Min has a probability of 100%, Min will always choose it
        if pr[index_max] == 1:
            return scores[index_max]

        # Otherwise, we have to do some work
        # We don't need to include actions that have a score worse than the best 100% action
        # We can disclude an action from the calculation by setting its probability to 0
        idxs = [i for i in range(len(scores)) if pr[i] == 1]
        if len(idxs) > 0:
            cutoff = max([s for i, s in enumerate(scores) if i in idxs])
            pr = [0 if s > cutoff else p for p, s in zip(pr, scores)]
        
        # Calculate a weighted sum
        # Have to normalize probabilities since the sum may be > 100%
        total_p = sum(pr)
        return sum(p / total_p * s for p, s in zip(pr, scores))

    if state.to_move == 'MIN':
        # In this case, probability means the chance that Min is *able* to take an action
        index_min = min(range(len(scores)), key=scores.__getitem__)

        # If the best move for Min has a probability of 100%, Min will always choose it
        if pr[index_min] == 1:
            return scores[index_min]

        # Otherwise, we have to do some work
        # We don't need to include actions that have a score worse than the best 100% action
        # We can disclude an action from the calculation by setting its probability to 0
        idxs = [i for i in range(len(scores)) if pr[i] == 1]
        if len(idxs) > 0:
            cutoff = min([s for i, s in enumerate(scores) if i in idxs])
            pr = [0 if s < cutoff else p for p, s in zip(pr, scores)]

        # Calculate a weighted sum
        # Have to normalize probabilities since the sum may be > 100%
        total_p = sum(pr)
        return sum(p / total_p * s for p, s in zip(pr, scores))


    if state.to_move == 'CHANCE':
        # return sum(p * expectimax(result(state, a), depth - 1, cutoff_time, eval_fn) for a, p in zip(ac, pr))
        return sum(p * s for s, p in zip(scores, pr))


def choose_move(s, eval_fn, depth=1, time_limit=None, print_info=False):
    a = None

    cutoff_time = math.inf
    if time_limit:
        cutoff_time = time.time() + time_limit

    if s.to_move == 'MAX':
        v = -math.inf
    else:
        v = math.inf

    for action in actions(s):
        val = expectimax(result(s, action), depth, cutoff_time, eval_fn)
        if print_info:
            print(f"{action}: {val}")
        if (s.to_move == 'MAX' and val > v) or (s.to_move == 'MIN' and val < v):
            a, v = action, val

    return a

def agent_random(state):
    return random.choice(actions(state.percept()))

def agent_depth1(state):
    return choose_move(state.percept(), eval_fn=state_eval, depth=1, time_limit=None, print_info=False)

def agent_depth2(state):
    return choose_move(state.percept(), eval_fn=state_eval, depth=2, time_limit=None, print_info=False)

def agent_depth3(state):
    return choose_move(state.percept(), eval_fn=state_eval, depth=3, time_limit=None, print_info=False)

def agent_3seconds(state):
    return choose_move(state.percept(), eval_fn=state_eval, depth=100, time_limit=3, print_info=False)

def agent_1second(state):
    return choose_move(state.percept(), eval_fn=state_eval, depth=100, time_limit=1, print_info=False)


def play_game(agent1, agent2, print_info=False):
    game_state = State(player='MAX')
    
    if print_info:
        game_state.print()

    start_time = time.time()
    p1_move_times = []
    p2_move_times = []

    while not is_terminal(game_state):
        if print_info:
            print(f"{game_state.to_move}'s turn")

        if game_state.to_move == 'MAX':
            t0 = time.time()
            action = agent1(game_state)
            p1_move_times.append(time.time() - t0)

        elif game_state.to_move == 'MIN':
            t0 = time.time()
            action = agent2(game_state)
            p2_move_times.append(time.time() - t0)

        else:
            if game_state.future:
                action = f"FUTURE_{'_'.join([cards[c] for c in game_state.deck[-3:][::-1]])}"

            elif game_state.cat_card or game_state.replace_ek:
                ac = actions(game_state)
                probabilities = probablity(game_state, ac)
                action = random.choices(ac, weights=probabilities)[0]

            else:
                # CHANCE - draw card
                action = f"DRAW_{cards[game_state.deck[-1]]}"

        if print_info:
            print(f"Chose action {action}")

        game_state = result(game_state, action)

        if print_info:
            game_state.print()

    stats = {
        'winner': 'P1' if utility(game_state) > 0 else 'P2',
        'total_time': time.time() - start_time,
        'p1_time': p1_move_times,
        'p2_time': p2_move_times,
        'total_actions': len(game_state.action_history),
        'player_actions': len(p1_move_times + p2_move_times),
        'remaining_cards': len(game_state.deck)
    }

    if print_info:
        game_state.print()
        if utility(game_state) > 0:
            print('MAX wins')
        else:
            print('MIN wins')

    return stats


def main():
    agents = {
        'agent_random': agent_random,
        'agent_depth1': agent_depth1,
        'agent_depth2': agent_depth2,
        'agent_depth3': agent_depth3,
        'agent_1second': agent_1second,
        'agent_3seconds': agent_3seconds
    }

    if len(sys.argv) < 3:
        print('Usage: python3 exploding_kittens.py <agent1> <agent2> [print_info]')
        print('print_info: True or False')
        print('Valid agents:')
        for k in agents.keys(): print(f'\t{k}')
        sys.exit(1)

    agent1 = sys.argv[1]
    agent2 = sys.argv[2]
    print_info = False
    if len(sys.argv) == 4:
        print_info = True if sys.argv[3] == 'True' else False

    results = play_game(agents[agent1], agents[agent2], print_info=print_info)
    print(f"Winner: {agent1 if results['winner'] == 'P1' else agent2} ({results['winner']})")


if __name__ == '__main__':
    main()
