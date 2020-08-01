from Utils import find_closing_bracket, BracketKinds
from enum import Enum, unique

class RegExPattern(object):
    def __init__(self, pattern, name=None):
        self.name = name
        self.pattern = []
        i = 0
        while i < len(pattern):
            set_end = 0

            requirement = None
            if pattern[i] == "(":
                set_end = find_closing_bracket(BracketKinds.PARENTHESES, pattern, i+1)
                requirement = RegExPattern(pattern[i+1:set_end]).pattern
            elif pattern[i] == "[":
                set_end = find_closing_bracket(BracketKinds.BRACKETS, pattern, i+1)
                if pattern[i+1] == "^":
                    pass #Next token is a negated set
                else:
                    pass #Next token is a normal set
            else:
                requirement = int(pattern[i:i+2], 16)

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
                    self.pattern.append((RegExModifiers.STAR, requirement))
            else:
                i = modifier_index
                self.pattern.append((RegExModifiers.NONE, requirement))

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
    print(RegExPattern("AA(AA+)", "lol").pattern)