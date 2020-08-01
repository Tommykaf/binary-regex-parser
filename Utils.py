from enum import Enum, unique


def find_closing_bracket(bracket_kind, string, start_index):
    stack = [start_index - 1]
    opening_index = start_index
    closing_index = start_index
    while len(stack) != 0:
        next_opening = string.find(bracket_kind.get_opening_bracket(), opening_index)
        next_closing = string.find(bracket_kind.get_closing_bracket(), closing_index)
        
        if ((next_opening != -1) and next_opening < next_closing):
            stack.append(next_opening)
            opening_index = next_opening + 1
        else:
            stack.pop()
            closing_index = next_closing + 1

    return closing_index - 1

@unique
class BracketKinds(Enum):
    PARENTHESES = ("(",")")
    BRACKETS = ("[","]")

    def get_opening_bracket(self):
        return self.value[0]

    
    def get_closing_bracket(self):
        return self.value[1]


if __name__ == "__main__":
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "()",1) == 1)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "((([])))",2) == 6)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "(assa((assa[asdsad]))sa)",1) == 23)
    assert(find_closing_bracket(BracketKinds.PARENTHESES, "(assa((assa[asdsad]))sa)",6) == 20)
    assert(find_closing_bracket(BracketKinds.BRACKETS, "((([])))",4) == 4)