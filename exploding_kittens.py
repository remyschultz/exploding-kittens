import random
from enum import Enum

Cards = Enum('Card', ['DEFUSE', 'EK', 'BCAT', 'WCAT', 'HCAT', 'RCAT', 'TCAT', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP'], start=0)
Actions = Enum('Action', ['DEFUSE', 'PAIR', 'ATTACK', 'FAVOR', 'NOPE', 'FUTURE', 'SHUFFLE', 'SKIP', 'DRAW'], start=0)
FULL_DECK = lambda: [4, 1, 4, 4, 4, 4, 4, 2, 4, 5, 5, 4, 4]

class ExplodingKittens:
    class State:
        def __init__(self, starting_hand=None):

            self.hands = {
                'MAX': {
                    'cards': starting_hand or self.generate_starting_hand(),
                    'size': 8
                },
                'MIN': {
                    'cards': [1] + ([0] * 12),
                    'size': 8
                }
            }
            self.deck = self.subtract_cards(FULL_DECK(), self.hands['MAX']['cards'], self.hands['MIN']['cards'])
            self.deck_size = 33
            self.top_deck = [-1] * 3
            self.ek_pos = -1
            self.active_played = []
            self.turns = 1 # for attack cards
            self.to_move = 'MAX'
            self.replace_ek = False
            self.favor = False

        def get_current_hand(self):
            return self.hands[to_move]['cards']

        def opposite_player(self):
            if self.to_move == 'MAX':
                return 'MIN'
            return 'MAX'

        def print(self):
            print("Max's Hand:")
            for card in Cards:
                print(f"\t{card.name}: {self.hands['MAX']['cards'][card.value]}")
            
            print("Min's Hand (known):")
            for card in Cards:
                print(f"\t{card.name}: {self.hands['MIN']['cards'][card.value]}")
            
            print("Deck (possible):")
            for card in Cards:
                print(f"\t{card.name}: {self.deck[card.value]}")
            
            print("Top three cards:")
            for card in self.top_deck:
                if card == -1:
                    print("\tUnknown")
                else:
                    print(f"\t{Cards(card).name}")
            
            print("Exploding Kitten position:")
            if self.ek_pos == -1:
                print("\tUnknown")
            else:
                print(f"\t{self.ek_pos}")
            
            print("Active action cards:")
            for card in self.active_played:
                print(f"\t{Cards(card).name}")
            if len(self.active_played) == 0:
                print("\tNone")
                
        def generate_starting_hand(self):
            hand = [0] * 13
            hand[Cards.DEFUSE.value] = 1

            deck = FULL_DECK()
            for _ in range(7):
                card = random.choice([i for i in range(len(deck)) if i > 1 and deck[i] > 0])
                hand[card] += 1
                deck[card] -= 1
            
            return hand

        def subtract_cards(self, a, *b):
            for bb in b:
                for i in range(len(a)):
                    a[i] -= bb[i]
            return a

        def add_cards(self, a, *b):
            for bb in b:
                for i in range(len(a)):
                    a[i] += bb[i]
            return a


    def actions(state):
        # Chance node - return all drawable cards
        if state.to_move == 'CHANCE':
            return [f'DRAW_{Cards(card).name}' for card, count in enumerate(state.deck) if count != 0]

        # Player just used Defuse - put the EK back into deck
        if state.replace_ek:
            return [f'REPLACE_{pos}' for pos in range(state.deck_size)]

        # Other player played Favor - must give a card to them
        if state.favor:
            return [f'GIVE_{Cards(card).name}' for card, count in enumerate(state.get_current_hand()) if count != 0]

        # Player drew EK - do they have Defuse?
        if state.get_current_hand()[Cards.EK.value] == 1:
            if state.get_current_hand()[Cards.EK.value] > 0:
                return ['DEFUSE']
            else:
                return []

        # Normal turn - can draw a card or play a card
        actions = ['DRAW']
        for card, count in enumerate(state.get_current_hand()):
            if card <= 1:
                # Defuse or EK - ignore
                continue
            if card <= 6:
                # Cat cards - need 2
                if count >= 2:
                    actions.append(Cards(card).name)
            if card == Cards['NOPE'].value:
                # Nope card - can only play if there was a previous 'action' card
                if count >= 1 and state.active_played:
                    actions.append('NOPE')
            else:
                # All other cards
                if count >= 1:
                    actions.append(Cards(card).name)

        return actions
    
    # def result(state, action):
    #     result_state = state.copy()

    #     if action == 'DEFUSE':
    #         result_state.replace_ek = True

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
        pass
    
    def utility(state, player):
        pass
    
    def eval(state, player):
        pass


def main():
    ek = ExplodingKittens()
    s = ek.State()
    s.print()


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