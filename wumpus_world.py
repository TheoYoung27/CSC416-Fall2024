"""
We want to write a program that consists of
1. The Wumpus World
2. A Player / Agent that has limited visibility of the world but can collect percepts
and perform logic inference.

"""

class World:
    """
    The Wumpus World.    
    """
    def __init__(self):
        """
        Initialize the state of the game, where the Wumpus is, where the pits are, etc.
        Represent the entities in the world, 
        - Maybe 2d array to represent the grid. 
        """
        self.facts = set()

    def ask(self, sentence):
        """
        Return whether the given sentence input is true in the World.
        For example, we want to be able to ask, W[1,1]? Then return False if no wumpus.
        """
        if isinstance(sentence, str):
            return sentence in self.facts

        operator, *operands = sentence

        if operator == 'NOT':
            return not self.ask(operands[0])
        elif operator == 'AND':
            return all(self.ask(op) for op in operands)
        elif operator == 'OR':
            return sentence in self.facts or any(self.ask(op) for op in operands)
        elif operator == 'IMPLIES':
            # p => q means either not p or q
            return not self.ask(operands[0]) or self.ask(operands[1])
        elif operator == 'IFF':
            return self.ask(operands[0]) == self.ask(operands[1])        

    def tell(self, sentence):
        """
        Give the world a sentence and tell it that this sentence is true.
        """
        self.facts.add(sentence)


class Player:
    """
    The Player in the Wumpus World.
    The Player should be able to (1) have a knowledge base, and (2) make inferences

    """
    def __init__(self, kb):
        self.kb = kb

    def make_inferences(self, query):
        """
        Given the Player's knowledge base, determine whether the given query is true.
        """
        facts, implications, bidirectionals = self._transform_kb()

        # set up a flag that tells us if we need to derive new propositions
        world = World()

        # add the base facts to the world
        for fact in facts:
            world.tell(fact)

        more_to_derive = True
        while more_to_derive:
            more_to_derive = False

            for premise, conclusion in implications:
                if world.ask(premise) and not world.ask(conclusion):
                    world.tell(conclusion)
                    more_to_derive = True

            for a, b in bidirectionals:
                # processing 'B11', ('OR', 'P12', 'P21')
                if world.ask(a) and not world.ask(b):
                    world.tell(b)
                    more_to_derive = True     
                if world.ask(b) and not world.ask(a):
                    world.tell(a)  
                    more_to_derive = True
        
        return world.ask(query)
    
    def _transform_kb(self):
        """
        Transform the knowledge to seperate its sentences into facts,
        implications, and bidirectionals
        """
        facts = set()
        implications = []
        bidirectionals = []

        for sentence in self.kb:
            if isinstance(sentence, str):
                # singleton strings represent simple facts 
                facts.add(sentence)
            elif isinstance(sentence, tuple):
                connective = sentence[0]
                if connective == 'IMPLIES':
                    premise, conclusion = sentence[1:]
                    implications.append((premise, conclusion))
                elif connective == 'IFF':
                    a, b = sentence[1:]
                    bidirectionals.append((a, b))
                elif connective == 'AND':
                    facts.add(sentence[1])
                    facts.add(sentence[2])
                else:
                    pass

        return facts, implications, bidirectionals

if __name__ == '__main__':
    # the initial knowledge base for the player
    initial_kb = [
        'A',
        ('IMPLIES', 'A', 'B'),
        ('NOT', 'P11'),
        ('NOT', 'W11'),
        ('NOT', 'B11'),
        ('NOT', 'S11'),
        ('IFF', 'B11', ('OR', 'P12', 'P21'))
    ]
    # our question - is there a pit in [2,1] (so that we can move there)
    query = 'P21' # we expect the answer to be False or ('NOT', 'P21') to be true
    # kb = {"1.1": [not p, not w, not b, not s]}
    player = Player(kb=initial_kb)
    print('This is the latest version')
    print(player.make_inferences(query)) # -> either True or False
