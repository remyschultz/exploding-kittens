import random, math
from enum import Enum
from copy import deepcopy

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

default_counts = [0,       4,    1,      4,      4,      4,      4,      4,        2,      4,       4,        5,         4,      4]

cards = ['UNKNOWN', 'DEFUSE', 'EK', 'BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP']

counts = [       0,        4,    1,      0,      0,      0,      0,      0,        2,      0,       0,        0,         0,      4]
start_hand_size = 3

FULL_DECK = lambda: deepcopy(counts)

class State:
    def __init__(self, starting_hand=None, player='MAX'):
        # self.pool = FULL_DECK()
        # self.max_hand = self.deal_hand()
        # self.min_hand = self.deal_hand()

        # self.deck = []
        # for card, count in enumerate(self.pool):
        #     self.deck += [card] * count
        # random.shuffle(self.deck)
        self.deal_cards()

        self.known_max = [start_hand_size - 1, 1] + ([0] * 12)
        self.known_min = [start_hand_size - 1, 1] + ([0] * 12)

        self.max_known_deck = []
        self.min_known_deck = []

        self.turns = 1 # for attack cards
        self.attack = False

        self.ek_pos = -1
        self.active_played = []
        self.to_move = player
        self.replace_ek = False
        self.favor = False # for cat cards
        self.drawing = None
        self.played = []

    # Min should perceive themselves as Max
    def percept(self):
        state = deepcopy(self)
        if self.to_move == 'MAX':
            state.deck = [state.deck[i] if i in state.max_known_deck else UNKNOWN for i in range(len(state.deck))]
            add_to_pool = State.subtract_cards(state.min_hand, state.known_min)
            add_to_pool[UNKNOWN] = 0
            state.pool = State.add_cards(state.pool, add_to_pool)
            state.min_hand = deepcopy(self.known_min)
            
            # state.min_known_ek = -1
            # state.min_known_top = []
        else:
            state.deck = [UNKNOWN if i not in self.min_known_deck else self.deck[i] for i in range(len(self.deck))]
            add_to_pool = State.subtract_cards(state.max_hand, state.known_max)
            add_to_pool[UNKNOWN] = 0
            state.pool = State.add_cards(state.pool, add_to_pool)
            state.max_hand = deepcopy(self.known_max)

            # state.max_known_ek = -1
            # state.max_known_top = []
        return state

    # def get_top_card(self):
    #     if self.to_move == 'MAX':
    #         if len(state.max_known_top) > 0:
    #             return state.max_known_top[0]

    #     elif self.to_move == 'MIN':
    #         if len(state.min_known_top) > 0:
    #             return state.min_known_top[0]

    #     return UNKNOWN

    def deal_cards(self):
        deck = FULL_DECK()
        deck[EK] = 0
        deck[DEFUSE] = 0

        self.deck = []
        for card, count in enumerate(deck):
            self.deck += [card] * count
        random.shuffle(self.deck)

        # print(self.deck)
        self.max_hand = [0] * len(counts)
        self.min_hand = [0] * len(counts)

        for card in self.deck[0 : start_hand_size - 1]:
            self.max_hand[card] += 1
        self.max_hand[DEFUSE] = 1

        for card in self.deck[start_hand_size - 1 : 2 * start_hand_size - 2]:
            self.min_hand[card] += 1
        self.min_hand[DEFUSE] = 1

        # print(self.max_hand)
        # print(self.min_hand)


        self.deck = self.deck[2 * start_hand_size - 2 :] + [EK] * counts[EK] + [DEFUSE] * (counts[DEFUSE] - 2)
        random.shuffle(self.deck)

        # print(self.deck)

        self.pool = State.subtract_cards(FULL_DECK(), self.max_hand, self.min_hand)

        # print(self.pool)

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
                self.known_max[UNKNOWN] -= 1
            else:
                self.known_max[card] -= count
        else:
            self.min_hand[card] -= count
            if self.known_min[card] == 0:
                self.known_min[UNKNOWN] -= 1
            else:
                self.known_min[card] -= count

    def opposite_player(self):
        if self.to_move == 'MAX':
            return 'MIN'
        return 'MAX'

    # def deck_size(self):
    #     return sum(self.pool) - self.max_hand[UNKNOWN] - self.min_hand[UNKNOWN]

    def print(self):
        print('--------STATE--------')
        print(f"{self.to_move}'s turn")
        print("Max's Hand:")
        for card in cards:
            if self.max_hand[cards.index(card)] > 0:
                print(f"\t{card}: {self.max_hand[cards.index(card)]}")

        print("Known Max:")
        for card in cards:
            if self.known_max[cards.index(card)] > 0:
                print(f"\t{card}: {self.known_max[cards.index(card)]}")
        
        print("Min's Hand:")
        for card in cards:
            if self.min_hand[cards.index(card)] > 0:
                print(f"\t{card}: {self.min_hand[cards.index(card)]}")

        print("Known Min:")
        for card in cards:
            if self.known_min[cards.index(card)] > 0:
                print(f"\t{card}: {self.known_min[cards.index(card)]}")
        
        print("Pool:")
        for card in cards:
            if self.pool[cards.index(card)] > 0:
                print(f"\t{card}: {self.pool[cards.index(card)]}")
        
        print("Deck:")
        print([cards[c] for c in self.deck])
        # for card in self.deck:
        #     print(f"\t{cards[card]}: {self.pool[cards.index(card)]}")

        print(f"Deck size: {len(self.deck)}")

        print(f"Played: {self.played}")


        print('---------------------\n')
        
        # print("Top three cards:")
        # for card in self.top_deck:
        #     if card == -1:
        #         print("\tUnknown")
        #     else:
        #         print(f"\t{Cards(card).name}")
        
        # print("Exploding Kitten position:")
        # if self.ek_pos == -1:
        #     print("\tUnknown")
        # else:
        #     print(f"\t{self.ek_pos}")
        
        # print("Active action cards:")
        # for card in self.active_played:
        #     print(f"\t{Cards(card).name}")
        # if len(self.active_played) == 0:
        #     print("\tNone")
            
    # def generate_starting_hand(deck=FULL_DECK()):
    #     hand = [0] * 14
    #     hand[DEFUSE] = 1

    #     # deck = FULL_DECK()
    #     for _ in range(start_hand_size - 1):
    #         card = random.choice([i for i in range(len(deck)) if i > EK and deck[i] > 0])
    #         hand[card] += 1
    #         deck[card] -= 1
        
    #     return hand

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
        if a.startswith('DRAW_'):
            card = cards.index(a.split('_', 1)[1])
            ps[i] = state.pool[card] / sum(state.pool)
        
        if a == 'DRAW':
            ps[i] = 1
        
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
    # Chance node - return all drawable cards
    if state.to_move == 'CHANCE':
        card = state.deck[-1]

        if card != UNKNOWN:
            return [f'DRAW_{cards[card]}']

        if sum(state.pool) == state.max_hand[UNKNOWN] + state.min_hand[UNKNOWN] + 1:
            # Only the EK remains in the actual deck
            return ['DRAW_EK']
        return [f'DRAW_{cards[card]}' for card, count in enumerate(state.pool) if count > 0]

    hand = deepcopy(state.get_current_hand())
    
    # This is to determine what actions the player could possibly take, given that their opponent may not know exactly what cards they have
    # if state.to_move == 'MIN':
    for card, count in enumerate(state.pool):
        if card != EK:
            hand[card] += min(count, hand[UNKNOWN])

    

    # Player just used Defuse - put the EK back into deck
    # if state.replace_ek:
    #     return [f'REPLACE_{pos}' for pos in range(sum(state.deck))]

    # Other player played Favor - must give a card to them
    # if state.favor: # for cat cards
    #     return [f'GIVE_{cards[card]}' for card, count in enumerate(hand) if count != 0]

    # Player drew EK - do they have Defuse?
    if hand[EK] == 1:
        if hand[DEFUSE] > 0 or (hand[UNKNOWN] > 0 and state.pool[DEFUSE] > 0):
            return ['DEFUSE']
        else:
            return []

    # Normal turn - can draw a card or play a card
    actions = []
    if len(state.deck) > 0:
        actions.append('DRAW')
    for card, count in enumerate(hand):
        # print(card, cards[card], count)
        if card <= DEFUSE:
            # Defuse or EK - ignore
            continue
        # elif card <= TCAT:
        #     # Cat cards - need 2
        #     if count >= 2:
        #         actions.append(cards[card])
        # elif card == NOPE:
        #     # Nope card - can only play if there was a previous 'action' card
        #     if count >= 1 and state.active_played:
        #         actions.append('NOPE')
        elif card == ATTACK:
            # no stacking attacks
            if count >= 1 and not state.attack:
                actions.append('ATTACK')
        else:
            # All other cards
            if count >= 1:
                actions.append(cards[card])

    return actions

def result(state, action):
    if action == None:
        return state
    
    result_state = deepcopy(state)

    result_state.played = [f"{state.to_move}: {action}"] + state.played

    if action == 'DRAW':
        result_state.drawing = state.to_move
        result_state.to_move = 'CHANCE'
        return result_state

    elif action.startswith('DRAW_'):

        result_state.deck.pop()

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
        

    card = cards.index(action)

    

    # MIN might have played a card we didn't know they had
    # if state.to_move == 'MIN' and state.min_hand[card] == 0:
            # result_state.min_hand[UNKNOWN] -= 1
    if state.get_current_hand()[card] == 0:
        result_state.remove_from_hand(UNKNOWN)
        # If a player plays a card that they don't for sure have, it must get removed from the pool
        result_state.pool[card] -= 1
    else:
        result_state.remove_from_hand(card)

    if action == 'DEFUSE':
        result_state.remove_from_hand(EK)
        result_state.pool[EK] += 1 # Put the EK back in the deck
        # Put EK into deck randomly
        result_state.deck.insert(random.randrange(len(result_state.deck)+1), EK)
        # Reset known deck info
        result_state.max_known_deck = []
        result_state.min_known_deck = []

        result_state.to_move = state.opposite_player()
        
    # elif action.startswith('GIVE'):
    #     card = Cards[action.split('_',1)[1]].value
    #     result_state.remove_from_hand(card)
    #     result_state.add_to_hand(state.opposite_player(), card)

    #     result_state.to_move = state.opposite_player()
    #     result_state.give = False

    # non-stacking for now
    elif action == 'ATTACK':
        result_state.to_move = state.opposite_player()
        result_state.attack = True
        if state.turns == 1:
            result_state.turns = 2
        else:
            result_state.turns += 2

    elif action == 'SKIP':
        if not state.attack: # state.turns == 1:
            result_state.to_move = state.opposite_player()
        else:
            result_state.attack = False
            result_state.turns -= 1

    # elif action == 'FUTURE':
    #     pass # make it chance's turn? then need to distinguish between drawing and seeing the future

    # elif action[1:] == 'CAT':
    #     result_state.remove_from_hand(Cards[action].value, 2)
    #     if state.to_move == 'MAX':
            # recieve random card from MIN

    # elif action == 'NOPE':
    #     if state.attack:
       
    return result_state


#     if action.startswith('REPLACE'):
#         result_state.replace_ek = False
#         result_state.max_hand[Cards.EK.value] == 0
#         result_state.ek_pos = int(action.split('_', 1)[1])
#         result_state.to_move = Players.MIN


def is_terminal(state):
    return state.max_hand[EK] == 1 and state.max_hand[DEFUSE] == 0 and (state.max_hand[UNKNOWN] == 0 or state.pool[DEFUSE] == 0) \
        or state.min_hand[EK] == 1 and state.min_hand[DEFUSE] == 0 and (state.min_hand[UNKNOWN] == 0 or state.pool[DEFUSE] == 0) 

def utility(state):
    if state.max_hand[DEFUSE] == 0 and state.max_hand[EK] == 1:
        return -10000
    if state.min_hand[DEFUSE] == 0 and state.min_hand[EK] == 1:
        return 10000
    return 0 # should never occur

def state_eval(state):
    score = 0
    
    # ek_prob = 1
    # if sum(state.pool) > 0:
    #     ek_prob = state.pool[EK] / sum(state.pool)

    score += 2 * (state.max_hand[SKIP] - state.min_hand[SKIP])
    score += 4 * (state.max_hand[ATTACK] - state.min_hand[ATTACK])
    score += 8 * (state.max_hand[DEFUSE] - state.min_hand[DEFUSE])

    score += 3 * (state.max_hand[UNKNOWN] - state.min_hand[UNKNOWN])

    score += -8 * (state.max_hand[EK] - state.min_hand[EK])

    return score

def expectimax(state, depth):
    if depth == 0:
        return state_eval(state)
    if is_terminal(state):
        return utility(state)

    ac = actions(state)
    scores = [expectimax(result(state, a), depth - 1) for a in ac]
    if len(scores) == 0:
        print(ac)
        print(is_terminal(state))
        state.print()
        # input()
        
    if state.to_move == 'MAX':
        # In this case, probability means the chance that Min is *able* to take an action
        # ac = actions(state)
        pr = probablity(state, ac)

        # scores = [expectimax(result(state, a), depth - 1) for a in ac]
        # if len(scores) == 0:
        #     print(ac)
        #     print(is_terminal(state))
        #     state.print()
        #     input()
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
        # if total_p == 0:
        #     print(ac)
        #     print(pr)
        #     state.print()
        #     input()
        return sum(p / total_p * s for p, s in zip(pr, scores))

        # return max(expectimax(result(state, a), depth - 1) for a in actions(state))

    if state.to_move == 'MIN':
        # In this case, probability means the chance that Min is *able* to take an action
        # ac = actions(state)
        pr = probablity(state, ac)

        # scores = [expectimax(result(state, a), depth - 1) for a in ac]
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
        if total_p == 0:
            print(ac)
            print(pr)
            state.print()
            input()
        return sum(p / total_p * s for p, s in zip(pr, scores))
        
        # return min(expectimax(result(s, a), depth - 1) for a in actions(s))


    if state.to_move == 'CHANCE':
        ac = actions(state)
        pr = probablity(state, ac)
        return sum(p * expectimax(result(state, a), depth - 1) for a, p in zip(ac, pr))

def choose_move(s):
    a = None

    if s.to_move == 'MAX':
        v = -math.inf
    else:
        v = math.inf

    for action in actions(s):
        val = expectimax(result(s, action), 8)
        print(f"{action}: {val}")
        if (s.to_move == 'MAX' and val > v) or (s.to_move == 'MIN' and val < v):
            a, v = action, val

    return a


def main():
    game_state = State(player='MAX')

    game_state.print()
    print(state_eval(game_state))

    while not is_terminal(game_state):
        print(f"{game_state.to_move}'s turn")

        if game_state.to_move in ['MAX', 'MIN']:
            action = choose_move(game_state.percept())

        else:
            # CHANCE - draw card
            draw_actions = actions(game_state)
            probabilities = probablity(game_state, draw_actions)
            action = random.choices(draw_actions, weights=probabilities)[0]

        print(f"Chose action {action}")

        game_state = result(game_state, action)

        game_state.print()

    game_state.print()
    if utility(game_state) > 0:
        print('MAX wins')
    else:
        print('MIN wins')


if __name__ == '__main__':
    main()
