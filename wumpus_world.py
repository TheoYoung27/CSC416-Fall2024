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

    def inference_by_resolution(self, query):
        """if converted query is in kb, return true, else return false?"""

    def resolve(self, cnf_1, cnf_2):
        """doesn't need to do much besides resolve not x and x in cnf_1 and cnf_2?
            needed for handling inference_by_resolution"""

    def convert_to_cnf(self, prop):
        """Simple statement case, return statement"""
        if(not isinstance(prop, str)):
            operator = prop[0]

            if(operator == 'IMPLIES'):
                """convert to form [or, (not prop[1]), prop[2]]"""
                return self.convert_to_cnf(['OR', ('NOT', prop[1]), prop[2]])
            
            elif(operator == 'AND'):
                """simple case, and contains atomic elements, return each element"""
                if(isinstance(prop[1], str) and isinstance(prop[2], str)):
                    return prop[1], prop[2]
                else:
                    return [self.convert_to_cnf(prop[1]), self.convert_to_cnf(prop[2])]
                
            elif(operator == 'IFF'):
                return self.convert_to_cnf(['AND', ('OR', ('NOT', prop[1]), prop[2]), ('OR', prop[1], ('NOT', prop[2]))])

            elif(operator == 'OR'):
                """case where or contains atomics - nothing to be done"""
                if(len(prop[1]) <= 1) and (len(prop[2]) <= 1):
                    return prop
                    """distributive case - ['OR', ('AND', 'X', 'Y'), 'Z'] converts to ['AND', ('OR', 'X', 'Z'), ('OR', 'Y','Z')]"""
                elif(prop[1][0] == 'AND'):
                    return self.convert_to_cnf(['AND', ('OR', prop[1][1], prop[2]), ('OR', prop[1][2], prop[2])])
                else:
                    """complex case, call convert on both operands"""
                    return ['OR', self.convert_to_cnf(prop[1]), self.convert_to_cnf(prop[2])]
                """catch nots, and props with nothing but variables -- need demorgan's case for nots"""
            elif(operator == 'NOT' and not isinstance(prop[1], str)):
                """double negation - remove and call convert on prop[1][1]"""
                if prop[1][0] == 'NOT':
                    return self.convert_to_cnf(prop[1][1])
        
                    """and - convert to ['OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])]"""
                elif prop[1][0] == 'AND':
                    return self.convert_to_cnf(['OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])])
        
                    """implies - convert to ['AND', prop[1][1], ('NOT', prop[1][2])"""
                elif prop[1][0] == 'IMPLIES':
                    return self.convert_to_cnf(['AND', prop[1][1], ('NOT', prop[1][2])])
        
                    """or - convert to ['AND', ('NOT', prop[1][1]), ('NOT', prop[1][2])]"""
                elif prop[1][0] == 'OR':
                    self.convert_to_cnf(['AND', ('NOT', prop[1][1]), ('NOT', prop[1][2])])

                    """iff - convert to ['AND', ('OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])), ('OR', prop[1][1], prop[1][2])]"""
                elif prop[1][0] == 'IFF':
                    self.convert_to_cnf(['AND', ('OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])), ('OR', prop[1][1], prop[1][2])])
        else:
            return prop
                
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
        """ transform kb into cnf!"""
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
        ['AND', ('AND', 'X', 'Y'), ('AND', 'A', 'B')], 'Z'
    ]
    # our question - is there a pit in [2,1] (so that we can move there)
    query = 'P21' # we expect the answer to be False or ('NOT', 'P21') to be true
    # kb = {"1.1": [not p, not w, not b, not s]}
    player = Player(kb=initial_kb)
    print('This is the latest version')
    prev_kb = None
    print(player.convert_to_cnf(['IMPLIES', ('NOT', 'A'), 'B']))
    print(player.convert_to_cnf(['NOT', 'A']))
    print(player.convert_to_cnf(['OR', ('AND', 'X', 'Y'), 'B']))
"""    print(player.make_inferences(query)) # -> either True or False"""