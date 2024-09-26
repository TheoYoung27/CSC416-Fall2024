class Player:
    """
    The Player in the Wumpus World.
    The Player should be able to (1) have a knowledge base, and (2) make inferences

    """
    def __init__(self, kb):
        self.kb = kb

    # doesn't work
    def inference_by_resolution(self, query):
        converted_kb = []
        for x in self.kb:
            y = self.convert_to_cnf(x[0])
            if(not isinstance(y, list)):
                y = [y]
            converted_kb.append(y)
        self.resolve(converted_kb[0], converted_kb[1])
        negated_query = self.convert_to_cnf(['NOT', query])
        return negated_query
        

    # doesn't work
    def resolve(self, cnf_1, cnf_2):
        # only handle cases where cnf_1 is atomic or negation of atomic
        resolved = set()
        for clause1 in cnf_1:
            for clause2 in cnf_2:
                if(isinstance(clause1, str) and clause2[0] == 'OR' and (clause2[1] == ('NOT', clause1) or ('NOT', clause2[1]) == clause1)):
                    resolved.add(clause2[2])
                    resolved.add(clause1)
                elif(isinstance(clause2, str) and clause1[0] == 'OR' and (clause1[1] == ('NOT', clause2) or ('NOT', clause1[1]) == clause2)):
                    resolved.add(clause1[2])
                    resolved.add(clause2)
        return resolved
                    

    def convert_to_cnf(self, prop):
        """Simple statement case, return statement"""
        if(not isinstance(prop, str)):
            operator = prop[0]

            if(operator == 'IMPLIES'):
                """convert to form [or, (not prop[1]), prop[2]]"""
                return self.convert_to_cnf(('OR', ('NOT', prop[1]), prop[2]))
            
            elif(operator == 'AND'):
                if(len(prop) == 2):
                    return prop[1]
                elif(len(prop) == 1):
                    return ()
                elif(prop[1] == prop[2]):
                    return ()
                """simple case, and contains atomic elements, return each element"""
                if(isinstance(prop[1], str) and isinstance(prop[2], str)):
                    return (prop[1], prop[2])
                
                    """case for prop and not prop - contradiction, return empty set"""
                elif(prop[1][0] == 'NOT' and prop[2] == prop[1][1]):
                    return ()
                                
                else:
                    return self.convert_to_cnf(prop[1]), self.convert_to_cnf(prop[2])
                
            elif(operator == 'IFF'):
                return self.convert_to_cnf(('AND', ('IMPLIES', prop[1], prop[2]), ('IMPLIES', prop[2], prop[1])))

            elif(operator == 'OR'):
                if(len(prop) == 2):
                    return prop[1]
                elif(len(prop) == 1):
                    return ()
                elif(prop[1] == prop[2]):
                    return ()
                """case where or contains atomics - nothing to be done"""
                if(len(prop[1]) <= 1) and (len(prop[2]) <= 1):
                    return ('OR', prop[1], prop[2])
                
                    """distributive case - ['OR', ('AND', 'X', 'Y'), 'Z'] converts to ['AND', ('OR', 'X', 'Z'), ('OR', 'Y','Z')]"""
                elif(prop[1][0] == 'AND'):
                    return self.convert_to_cnf(('OR', prop[1][1], prop[2]), ('OR', prop[1][2], prop[2]))
                
                else:
                    """complex case, call convert on both operands"""
                    return ('OR', self.convert_to_cnf(prop[1]), self.convert_to_cnf(prop[2]))
                """catch nots, and props with nothing but variables -- need demorgan's case for nots"""
            elif(operator == 'NOT'):

                """double negation - remove and call convert on prop[1][1]"""
                if prop[1][0] == 'NOT':
                    if(isinstance(prop[1][1], str)):
                        return (prop[1][1])
                    else:
                        return self.convert_to_cnf(prop[1][1])
        
                    """and - convert to ['OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])]"""
                elif prop[1][0] == 'AND':
                    return self.convert_to_cnf(('OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])))
        
                    """implies - convert to ['AND', prop[1][1], ('NOT', prop[1][2])"""
                elif prop[1][0] == 'IMPLIES':
                    return self.convert_to_cnf(('AND', prop[1][1], ('NOT', prop[1][2])))
        
                    """or - convert to ['AND', ('NOT', prop[1][1]), ('NOT', prop[1][2])]"""
                elif prop[1][0] == 'OR':
                    return self.convert_to_cnf(('AND', ('NOT', prop[1][1]), ('NOT', prop[1][2])))

                    """iff - convert to ['AND', ('OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])), ('OR', prop[1][1], prop[1][2])] --- problem"""
                elif prop[1][0] == 'IFF':
                    return self.convert_to_cnf(('AND', ('OR', ('NOT', prop[1][1]), ('NOT', prop[1][2])), ('OR', prop[1][1], prop[1][2])))
                else:
                    return ('NOT', prop[1])
        return prop
                
if __name__ == '__main__':
    # the initial knowledge base for the player
    initial_kb = [
        [('NOT', 'B11')], [('IFF', 'B11', ('OR', 'P12', 'P21'))]
    ]
    # our question - is there a pit in [2,1] (so that we can move there)
    query = 'P21' # we expect the answer to be False or ('NOT', 'P21') to be true
    # kb = {"1.1": [not p, not w, not b, not s]}
    player = Player(kb=initial_kb)
    print('This is the latest version')
    print(player.convert_to_cnf(('IFF', 'B11', ('OR', 'P12', 'P21'))))
    print(player.convert_to_cnf(['AND', ('NOT', 'B11'), ('IFF', 'B11', ('OR', 'P12', 'P21'))]))
    print(player.convert_to_cnf(['AND', 'P', ['IMPLIES', 'P', 'Q']]))