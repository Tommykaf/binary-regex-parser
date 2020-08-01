from Utils import find_closing_bracket, BracketKinds
from enum import Enum, unique

class RegExPattern(object):
    possible_values = [i for i in range(256)]
    
    def __init__(self, pattern, name = None):
        self.name = name
        self.pattern = []
        self.last_non_forcing_index = 0
        self.initiators = None
        i = 0
        while i < len(pattern):
            set_end = 0

            requirement = []
            if pattern[i] == "(":
                set_end = find_closing_bracket(BracketKinds.PARENTHESES, pattern, i+1)
                requirement = RegExPattern(pattern[i+1:set_end])
            elif pattern[i] == "[" or pattern[i] == ".":
                if pattern[i] == ".":
                    requirement = RegExPattern.possible_values
                else:
                    set_end = find_closing_bracket(BracketKinds.BRACKETS, pattern, i+1)
                    j = i + 2
                    while j < set_end:
                        if pattern[j+2] == "-":
                            for byte in range(int(pattern[j-2 : j],16), \
                                int(pattern[j+1 : j+3],16)):
                                requirement.append(int(byte,16))
                            j += 5
                        else:
                            requirement.append(int(pattern[j:j+2],16))
                            j += 2

                    if pattern[i+1] == "^":
                        requirement = [elem for elem in RegExPattern.possible_values if elem not in requirement]

                        
            else:
                requirement = [int(pattern[i:i+2], 16)]

            if (self.initiators == None):
                if (type(requirement) is RegExPattern):
                    self.initiators = requirement.initiators
                elif (type(requirement) is list):
                    self.initiators = requirement

            if set_end != 0:
                modifier_index = set_end + 1
            else:
                modifier_index = i + 2

            if (modifier_index <= len(pattern) - 1 and pattern[modifier_index] in RegExModifiers.getModifiers()):
                i = modifier_index + 1
                if pattern[modifier_index] == RegExModifiers.STAR.value:
                    self.pattern.append((RegExModifiers.STAR, requirement))
                elif pattern[modifier_index] == RegExModifiers.QMARK.value:
                    self.pattern.append((RegExModifiers.QMARK, requirement))
                elif pattern[modifier_index] == RegExModifiers.PLUS.value:
                    self.pattern.append((RegExModifiers.NONE, requirement))
                    self.last_non_forcing_index = len(self.pattern) - 1
                    self.pattern.append((RegExModifiers.STAR, requirement))
                
            else:
                i = modifier_index
                self.pattern.append((RegExModifiers.NONE, requirement))
                self.last_non_forcing_index = len(self.pattern) - 1

    def __len__(self):
        return len(self.pattern)





@unique
class RegExModifiers(Enum):
    STAR = "*"
    QMARK = "?"
    PLUS = "+"
    NONE = None

    def get_opening_bracket(self):
        return self.value[0]

    
    def get_closing_bracket(self):
        return self.value[1]
    
    @staticmethod
    def getModifiers():
        return ["*","?","+"]


if __name__ == "__main__":
    assert(RegExPattern("AA", "lol").pattern == [(RegExModifiers.NONE, [int("AA",16)])])
    print(RegExPattern("[^AABB]", "lol").pattern)
    assert(RegExPattern("AABB", "lol").pattern == [(RegExModifiers.NONE, [int("AA",16)]),(RegExModifiers.NONE, [int("BB",16)])])
    assert(RegExPattern("AA*BB", "lol").pattern == [(RegExModifiers.STAR, [int("AA",16)]),(RegExModifiers.NONE, [int("BB",16)])])
    assert(RegExPattern("AA?BB", "lol").pattern == [(RegExModifiers.QMARK, [int("AA",16)]),(RegExModifiers.NONE, [int("BB",16)])])
    assert(RegExPattern("AA+BB", "lol").pattern == [(RegExModifiers.NONE, [int("AA",16)]),(RegExModifiers.STAR, [int("AA",16)]),(RegExModifiers.NONE, [int("BB",16)])])
