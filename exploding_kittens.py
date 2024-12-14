import random, math
from enum import Enum
from copy import deepcopy

default_counts = [0,       4,    1,      4,      4,      4,      4,      4,        2,      4,       4,        5,         4,      4]
cards = ['UNKNOWN', 'DEFUSE', 'EK', 'BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP']
counts = [       0,        4,    1,      0,      0,      0,      0,      0,        2,      0,       0,        0,         0,      4]
start_hand_size = 3

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

# Cards = Enum('Card', ['DEFUSE', 'EK', 'BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP'], start=0)
FULL_DECK = lambda: deepcopy(counts)

class State:
    def __init__(self, starting_hand=None, player='MAX'):

        # self.max_hand = starting_hand or State.generate_starting_hand()
        # self.min_hand = [start_hand_size - 1, 1] + ([0] * 12)

        # # self.deck = State.subtract_cards(FULL_DECK(), self.hands['MAX']['cards'], self.hands['MIN']['cards'])
        # self.deck = State.subtract_cards(FULL_DECK(), self.max_hand, self.min_hand)

        # self.deck_size = 33

        self.deal_cards()

        self.known_max = [start_hand_size - 1, 1] + ([0] * 12)
        self.known_min = [start_hand_size - 1, 1] + ([0] * 12)

        # self.known_deck_max = [UNKNOWN] * ???

        # self.top_deck = [-1] * 3
        self.ek_pos = -1
        self.active_played = []
        self.turns = 1 # for attack cards
        self.attack = False
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


    def deal_cards(self):
        self.deck = FULL_DECK()
        self.max_hand = State.generate_starting_hand(self.deck)
        self.min_hand = State.generate_starting_hand(self.deck)

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
        
        # print("Min's Hand (known):")
        # for card in Cards:
        #     print(f"\t{card.name}: {self.hands['MIN']['cards'][card.value]}")
        
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
            # if sum(state.deck) == 0:
            #     print(state.deck)
            #     print(a, card)
            #     print(state.played)
            ps[i] = state.deck[card] / sum(state.deck)
    return ps



def actions(state):
    # Chance node - return all drawable cards
    if state.to_move == 'CHANCE':
        return [f'DRAW_{cards[card]}' for card, count in enumerate(state.deck) if count > 0]
        
    # This is not a perfect solution. If we are at the start of the game, there's no way min can have 3 diffuse cards, for example.
    # Maybe we can track both the set of known cards and the set of possible cards?
    # We could then say that min's hand contains N cards from this set
    hand = state.get_current_hand()
    # known_count = sum(hand)
    if state.to_move == 'MIN':
        for card, count in enumerate(state.deck):
            if card != EK:
                hand[card] += min(count, hand[UNKNOWN])

    # print(hand)

    

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
    result_state = deepcopy(state)

    result_state.attack = False

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
            return result_state

        if result_state.turns != 1:
            result_state.turns -= 1
        else:
            result_state.to_move = state.opposite_player()

        return result_state
        
    #drawing removes from turns 

    card = cards.index(action)

    result_state.played = [f"{state.to_move}: {action}"] + state.played

    # MIN might have played a card we didn't know they had
    if state.to_move == 'MIN' and state.min_hand[card] == 0:
            result_state.min_hand[UNKNOWN] -= 1
    else:
        result_state.remove_from_hand(card)

    if action == 'DEFUSE':
        # result_state.remove_from_hand(Cards.DEFUSE.value)
        # result_state.replace_ek = True
        result_state.remove_from_hand(EK)
        result_state.deck[EK] += 1 # Put the EK back in the deck
        result_state.to_move = state.opposite_player()
        # return result_state
    
    # elif action.startswith('GIVE'):
    #     card = Cards[action.split('_',1)[1]].value
    #     result_state.remove_from_hand(card)
    #     result_state.add_to_hand(state.opposite_player(), card)

    #     result_state.to_move = state.opposite_player()
    #     result_state.give = False

    # non-stacking for now
    elif action == 'ATTACK':
        # result_state.remove_from_hand(Cards.ATTACK.value)
        result_state.to_move = state.opposite_player()
        result_state.attack = True
        if state.turns == 1:
            result_state.turns = 2
        else:
            result_state.turns += 2

    elif action == 'SKIP':
        # result_state.remove_from_hand(Cards.SKIP.value)
        if state.turns == 1:
            result_state.to_move = state.opposite_player()
        else:
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

#     if state.to_move == Players.MAX:
#         if action.type == play:

#             state.max_hand[action.card] -= 1
            
#             result_state.active_played.prepend(action.card)
#             state.reconcile_active_played() # remove unneccesary history

#             if action.card in attack, skip:
#                 result_state.to_move = MIN




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
        # s.print()
        ac = actions(s)
        # print(ac)
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
    # TODO: 
    #   add to state: each player's knowledge of the other player's hand and of the deck
    #   initalize hands


    game_state = State()

    while not is_terminal(game_state):

        if game_state.to_move == 'MAX':
            # p = game_state.percept('MAX')
            # action = choose_move(p)
            # p = result(p, a)
            # game_state.known_min = p.min_hand
            action = choose_move(game_state.percept())

        elif game_state.to_move == 'MIN':
            action = choose_move(game_state.percept())

        else:
            # CHANCE - draw card
            draw_actions = actions(game_state)
            probabilities = probablity(game_state, draw_actions)
            action = random.choices(draw_actions, weights=probabilities)[0]

        game_state = result(game_state, action)

    print(utility(game_state))
    if utility(game_state) == 1:
        print('MAX wins')
    else:
        print('MIN wins')



    # generate starting hands
    # h1, h2 = deal()

    # player = random.choice(['MAX', 'MIN'])

    # # create starting states - each player's model of the true state
    # s1 = State(h1, player)
    # s2 = State(h2, player)

    # # # player 1 goes first
    # # a = choose_move(s1)
    # # s1 = result(a)
    # # s2 = result(a)

    # while not is_terminal(s1) or not is_terminal(s2):
    #     if s1.to_move != s2.to_move:
    #         print('inconsistency!!!')
    #         return
        
    #     if s1.to_move == 'MAX':
    #         a = choose_move(s1)
    #         s1 = result(s1, a)
    #     else:
    #         a = choose_move(s2)

    #     s1 = result(s1, a)
    #     s2 = result(s2, a)

    # if utility(s1) == 1:
    #     print('MAX wins')
    # if utility(s2) == 1:
    #     print('MIN wins')




    # s = State()

    # while not is_terminal(s):
    #     s.print()
    #     a = choose_move(s)
    #     print(a)
    #     s = result(s, a)
    # print(utility(s))

    # s.deck = [0, 1, 1] + [0] * 10 + [1]
    # s.max_hand = [0] * 14
    # s.max_hand[SKIP] = 1
    # s.max_hand[ATTACK] = 1
    # s.min_hand = [0] * 14
    # s.min_hand[SKIP] = 1
    # s.min_hand[ATTACK] = 1
    # s.print()
    # print(choose_move(s))
    # s.max_hand[ATTACK] = 1
    # s.attack = True
    # s.to_move = 'CHANCE'
    # s.print()
    # a = actions(s)
    # print(a)
    # p = probablity(s, a)
    # print(p)
    # s.hands['MIN']['size'] = 3
    # s.hands['MIN']['cards'][1] = 1
    # s.print()
    # # print(actions(s))
    # for a in actions(s):
    #     print(a)
    #     result(s, a).print()
    #     print('\n\n')


if __name__ == '__main__':
    main()


'''
2x attack

4x beardcat
4x watermellon cat
4x hairy potato cat
4x rainbow ralphing cat
4x tacocat

4x defuse (2 players)
1x exploding kitten (2 players)

4x favor
5x nope
5x see the future
4x shuffle
4x skip
'''