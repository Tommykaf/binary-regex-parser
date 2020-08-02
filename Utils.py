from enum import Enum, unique


def find_closing_bracket(bracket_kind, string, start_index):
    '''Find the matching closing bracket's index in a given string for a bracket of kind bracket_kind
        
    Arguments:
        bracket_kind -- kind of bracket we are looking for, should be of class BracketKinds
        string -- the string in which the brackets are found
        start_index -- the index of the opening bracket
    
    Retruns:
        index of the matching closing bracket in the given string
    '''

    depth = 1
    opening_index = start_index + 1
    closing_index = start_index + 1

    # When the next bracket is a closing one, depth is decreased by 1, else increased by one
    # If depth is back to zero - then we have found our closing bracket 
    while depth > 0:
        next_opening = string.find(bracket_kind.get_opening_bracket(), opening_index)
        next_closing = string.find(bracket_kind.get_closing_bracket(), closing_index)
        
        if ((next_opening != -1) and next_opening < next_closing):
            depth += 1
            opening_index = next_opening + 1
        else:
            depth -= 1
            closing_index = next_closing + 1

    return closing_index - 1

@unique
class BracketKinds(Enum):
    PARENTHESES = ("(",")")
    BRACKETS = ("[","]")
    CURLY_BRACKETS = ("{","}")

    def get_opening_bracket(self):
        return self.value[0]

    
    def get_closing_bracket(self):
        return self.value[1]


if __name__ == "__main__":
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "()",0) == 1)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "((([])))",1) == 6)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "(assa((assa[asdsad]))sa)",0) == 23)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "(assa((assa[asdsad]))sa)",5) == 20)
    assert(find_closing_bracket(BracketKinds.BRACKETS, "((([])))",3) == 4)