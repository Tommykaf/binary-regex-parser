from Utils import BracketKinds
import Utils
from enum import Enum, unique

class RegExPattern(object):
    '''A Class representing a hexadecimal regex pattern'''
    
    base = 16
    possible_values = list(range(256))
    
    def __init__(self, pattern, name = None):
        self.name = name

        # A list of tuples of shape (MODIFIER,REQUIREMENT), each representing the next sub-pattern
        # These dictate the RegEx Expression
        self.pattern = []

        # The last sub-pattern that "must be there"
        # (i.e. it's modifier is not *, ? and so on...)
        self.last_forcing_index = 0
        
        # The bytes that this pattern can start with
        self.initiators = None
        
        i = 0
        while i < len(pattern):
            
            set_end = 0
            requirement = []
            modifier_index = 0

            # Look if the next character opens a complex sub-pattern, a capture group or a is character
            # if we have found parentheses - a complex sub-pattern is required
            if pattern[i] == BracketKinds.PARENTHESES.get_opening_bracket():
                set_end = Utils.find_closing_bracket(BracketKinds.PARENTHESES, pattern, i)
                requirement = RegExPattern(pattern[i+1:set_end])

            # brackets mean that we need a capture group
            elif pattern[i] == BracketKinds.BRACKETS.get_opening_bracket():
                    set_end = Utils.find_closing_bracket(BracketKinds.BRACKETS, pattern, i)
                    requirement = Utils.find_capture_group(pattern, i, set_end, RegExPattern.base, RegExPattern.possible_values)
            
            # "." is equivalent for a capture group of all possible values
            elif pattern[i] == ".":
                requirement = RegExPattern.possible_values
            
            # else just take the next 2 characters
            else:
                requirement = [int(pattern[i:i+2], RegExPattern.base)]

            # Initiators are always the first requirement
            # Either for thiis pattern of it's first sub pattern (recursively)
            if (self.initiators == None):
                if (type(requirement) is RegExPattern):
                    self.initiators = requirement.initiators
                elif (type(requirement) is list):
                    self.initiators = requirement

            if set_end != 0:
                modifier_index = set_end + 1
            else:
                modifier_index = i + 2

            # If tthe character following the requirement is a modifier
            # find which one is it and append tthe tuple to the set.
            if (modifier_index <= len(pattern) - 1 and pattern[modifier_index] in RegExModifiers.getModifiers()):
                i = modifier_index + 1
                if pattern[modifier_index] == RegExModifiers.STAR.value:
                    self.pattern.append((RegExModifiers.STAR, requirement))

                elif pattern[modifier_index] == RegExModifiers.QMARK.value:
                    self.pattern.append((RegExModifiers.QMARK, requirement))

                # A requirement with a "+" modifier is equvalent to
                # the same requirement witth no modifier
                # followed by itself with a "*" 
                elif pattern[modifier_index] == RegExModifiers.PLUS.value:
                    self.pattern.append((RegExModifiers.NONE, requirement))
                    self.last_forcing_index = len(self.pattern) - 1

                    self.pattern.append((RegExModifiers.STAR, requirement))
                
                # If there's a curly bracket next, it is equivalent to:
                # requirement{a} == a times "requirement"
                # requirement{a,b} == a times "requirement" followed by b-a times "requirement?"
                elif pattern[modifier_index] == RegExModifiers.CURLY_BRACKETS.value:
                    bracket_end = Utils.find_closing_bracket(BracketKinds.CURLY_BRACKETS, pattern, i)
                    comma_index = pattern.find(",",i+1,bracket_end)

                    if (comma_index != -1 and comma_index <= bracket_end):
                        minimum = int(pattern[modifier_index+1:comma_index])
                        maximum = int(pattern[comma_index+1:bracket_end])

                        self.pattern.extend([(RegExModifiers.NONE, requirement) for _ in range(minimum)])
                        self.last_forcing_index = len(self.pattern) - 1

                        self.pattern.extend([(RegExModifiers.QMARK, requirement) for _ in range(minimum, maximum)])

                    else:
                        repetitions = int(pattern[modifier_index+1:bracket_end])
                        self.pattern.extend([(RegExModifiers.NONE, requirement) for _ in range(repetitions)])

                    i = bracket_end + 1
                
            else:
                i = modifier_index
                self.pattern.append((RegExModifiers.NONE, requirement))
                self.last_forcing_index = len(self.pattern) - 1

    def __len__(self):
        return len(self.pattern)





@unique
class RegExModifiers(Enum):
    STAR = "*"
    QMARK = "?"
    PLUS = "+"
    CURLY_BRACKETS = "{"
    NONE = None

    def get_opening_bracket(self):
        return self.value[0]

    
    def get_closing_bracket(self):
        return self.value[1]
    
    @staticmethod
    def getModifiers():
        return ["*","?","+","{"]


if __name__ == "__main__":
    assert(RegExPattern("AA", "lol").pattern == [(RegExModifiers.NONE, [int("AA",RegExPattern.base)])])
    assert(RegExPattern("AA{2,4}", "lol").pattern == [(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.QMARK, [int("AA",RegExPattern.base)]),(RegExModifiers.QMARK, [int("AA",RegExPattern.base)])])
    assert(RegExPattern("AA{2}AA", "lol").pattern == [(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("AA",RegExPattern.base)])])
    assert(RegExPattern("AABB", "lol").pattern == [(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("BB",RegExPattern.base)])])
    assert(RegExPattern("AA*BB", "lol").pattern == [(RegExModifiers.STAR, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("BB",RegExPattern.base)])])
    assert(RegExPattern("AA?BB", "lol").pattern == [(RegExModifiers.QMARK, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("BB",RegExPattern.base)])])
    assert(RegExPattern("AA+BB", "lol").pattern == [(RegExModifiers.NONE, [int("AA",RegExPattern.base)]),(RegExModifiers.STAR, [int("AA",RegExPattern.base)]),(RegExModifiers.NONE, [int("BB",RegExPattern.base)])])
