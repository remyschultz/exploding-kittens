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
        self.deck = FULL_DECK()
        self.max_hand = self.deal_hand()
        self.min_hand = self.deal_hand()

        self.known_max = [start_hand_size - 1, 1] + ([0] * 12)
        self.known_min = [start_hand_size - 1, 1] + ([0] * 12)

        self.turns = 1 # for attack cards
        self.attack = False

        self.ek_pos = -1
        self.active_played = []
        self.to_move = player
        self.replace_ek = False
        self.favor = False # for cat cards
        self.drawing = None
        self.played = []

    def percept(self):
        state = deepcopy(self)
        if self.to_move == 'MAX':
            state.min_hand = self.known_min
        else:
            state.max_hand = self.known_max
        return state

    def deal_hand(self):
        hand = [0] * 14
        hand[DEFUSE] = 1
        self.deck[DEFUSE] -= 1

        for _ in range(start_hand_size - 1):
            card = random.choice([i for i in range(len(self.deck)) if i > EK and self.deck[i] > 0])
            hand[card] += 1
            self.deck[card] -= 1
        
        return hand

    def get_current_hand(self, player=None):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            return self.max_hand
        return self.min_hand

    def add_to_hand(self, card, player=None, count=1):
        if player == None:
            player = self.to_move
        if player == 'MAX':
            self.max_hand[card] += count
            self.known_max[card] += count
        else:
            self.min_hand[card] += count
            self.known_min[card] += count

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

    def print(self):
        print('--------STATE--------')
        print(f"{self.to_move}'s turn")
        print("Max's Hand:")
        for card in cards:
            if self.max_hand[cards.index(card)] > 0:
                print(f"\t{card}: {self.max_hand[cards.index(card)]}")
        
        print("Min's Hand:")
        for card in cards:
            if self.min_hand[cards.index(card)] > 0:
                print(f"\t{card}: {self.min_hand[cards.index(card)]}")
        
        print("Pool:")
        for card in cards:
            if self.deck[cards.index(card)] > 0:
                print(f"\t{card}: {self.deck[cards.index(card)]}")


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
            
    def generate_starting_hand(deck=FULL_DECK()):
        hand = [0] * 14
        hand[DEFUSE] = 1

        # deck = FULL_DECK()
        for _ in range(start_hand_size - 1):
            card = random.choice([i for i in range(len(deck)) if i > EK and deck[i] > 0])
            hand[card] += 1
            deck[card] -= 1
        
        return hand

    def subtract_cards(a, *b):
        for bb in b:
            for i in range(1, len(a)):
                a[i] -= bb[i]
        return a

    def add_cards(a, *b):
        for bb in b:
            for i in range(1, len(a)):
                a[i] += bb[i]
        return a

# returns a list of probabilities for each action
def probablity(state, actions):
    ps = [0] * len(actions)
    for i, a in enumerate(actions):
        if a.startswith('DRAW_'):
            card = cards.index(a.split('_', 1)[1])
            ps[i] = state.deck[card] / sum(state.deck)
    return ps



def actions(state):
    # Chance node - return all drawable cards
    if state.to_move == 'CHANCE':
        return [f'DRAW_{cards[card]}' for card, count in enumerate(state.deck) if count > 0]

    hand = state.get_current_hand()
    
    # This is to determine what actions Min could possibly take, given that Max doesn't know exactly what cards Min has.
    if state.to_move == 'MIN':
        for card, count in enumerate(state.deck):
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
        if hand[EK] > 0:
            return ['DEFUSE']
        else:
            return []

    # Normal turn - can draw a card or play a card
    actions = ['DRAW']
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

    if action == 'DRAW':
        result_state.drawing = state.to_move
        result_state.to_move = 'CHANCE'
        return result_state

    elif action.startswith('DRAW_'):
        result_state.to_move = state.drawing
        result_state.drawing = None


        card = cards.index(action.split('_', 1)[1])

        result_state.add_to_hand(card)
        result_state.deck[card] -= 1

        if card == EK:
            result_state.attack = False
            return result_state


        if state.attack:
            result_state.attack = False
        else:
            result_state.to_move = result_state.opposite_player()

        return result_state
        

    card = cards.index(action)

    result_state.played = [f"{state.to_move}: {action}"] + state.played

    # MIN might have played a card we didn't know they had
    if state.to_move == 'MIN' and state.min_hand[card] == 0:
            result_state.min_hand[UNKNOWN] -= 1
    else:
        result_state.remove_from_hand(card)

    if action == 'DEFUSE':
        result_state.remove_from_hand(EK)
        result_state.deck[EK] += 1 # Put the EK back in the deck
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
    return state.max_hand[DEFUSE] == 0 and state.max_hand[EK] == 1 or \
           state.min_hand[DEFUSE] == 0 and state.min_hand[EK] == 1

def utility(state):
    if state.max_hand[DEFUSE] == 0 and state.max_hand[EK] == 1:
        return -1
    if state.min_hand[DEFUSE] == 0 and state.min_hand[EK] == 1:
        return 1
    return 0 # should never occur

def state_eval(state):
    hand = state.max_hand

    if sum(state.deck) > 0:
        ek_prob = state.deck[EK] / sum(state.deck)

    elif state.min_hand[EK] == 1:
        ek_prob = 1
    else:
        ek_prob = 0

    return ek_prob * 10 * (hand[SKIP] + hand[ATTACK]) \
            + hand[DEFUSE] * 10 \
            + sum(state.max_hand) - sum(state.min_hand)

def expectimax(s, depth):
    if depth == 0:
        return state_eval(s)
    if is_terminal(s):
        return utility(s)
        
    if s.to_move == 'MAX':
        return max(expectimax(result(s, a), depth - 1) for a in actions(s))

    if s.to_move == 'MIN':            
        return min(expectimax(result(s, a), depth - 1) for a in actions(s))

    if s.to_move == 'CHANCE':
        ac = actions(s)
        pr = probablity(s, ac)
        return sum(p * expectimax(result(s, a), depth - 1) for a, p in zip(ac, pr))

def choose_move(s):
    a, v = None, -math.inf
    for action in actions(s):
        val = expectimax(result(s, action), 5)
        if val > v:
            a, v = action, val
    return a


def main():
    game_state = State()

    game_state.print()

    while not is_terminal(game_state):
        print(f"{game_state.to_move}'s turn")

        if game_state.to_move == 'MAX':
            action = choose_move(game_state.percept())

        elif game_state.to_move == 'MIN':
            action = choose_move(game_state.percept())

        else:
            # CHANCE - draw card
            draw_actions = actions(game_state)
            probabilities = probablity(game_state, draw_actions)
            action = random.choices(draw_actions, weights=probabilities)[0]

        print(f"Chose action {action}")
        input()

        game_state = result(game_state, action)

        game_state.print()

    game_state.print()
    if utility(game_state) == 1:
        print('MAX wins')
    else:
        print('MIN wins')


if __name__ == '__main__':
    main()
