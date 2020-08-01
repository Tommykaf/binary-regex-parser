from RegExPattern import RegExPattern, RegExModifiers

class RegExMatcher(object):
    
    def __init__(self, regex_pattern, start_index, base = 16):
        self.regex_pattern = regex_pattern
        self.start_index = start_index
        self.base = base
        self._valid = True
        self.is_done = False
        self.pattern_index = 0
        self.subpattern_matcher = None
        self.length = 0

    def isValid(self):
        return self._valid

    def isDone(self, cleanup = False):
        if (cleanup):
            self.is_done = self.is_done or self.pattern_index >= self.regex_pattern.last_non_forcing_index - 1
            if (self.subpattern_matcher != None):
                self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
        else:
            self.is_done = self.is_done or self.pattern_index >= len(self.regex_pattern.pattern)
        return self.is_done

    def info(self):
        return {
            "length": self.length,
            "name": self.regex_pattern.name,
            "indices": {
                "start": self.start_index,
                "end": self.start_index + self.length
            }
        }

    def _advance(self):
        if (self.pattern_index + 1 >= len(self.regex_pattern.pattern)):
            self.is_done = True
        else:
            self.pattern_index += 1

    def _reset(self):
        self.start_index = self.start_index + self.length
        self._valid = True
        self.is_done = False
        self.pattern_index = 0
        if (self.subpattern_matcher != None):
            self.subpattern_matcher._reset()
        self.length = 0


    def validate(self, nextByte):
        if (self.isDone()):
            return False

        nextByteValid = True
        if (type(nextByte) is str):
            nextByte = int(nextByte,self.base)
        
        current_modifier = self.regex_pattern.pattern[self.pattern_index][0]
        current_requirement = self.regex_pattern.pattern[self.pattern_index][1]
        
        if (type(current_requirement) is int):
            if (nextByte == current_requirement):
                self.length += 1
                if (current_modifier != RegExModifiers.STAR):
                    self._advance()
            elif (current_modifier == RegExModifiers.STAR or
                    current_modifier == RegExModifiers.QMARK):
                    self._advance()
                    if (not self.isDone()):
                        self.validate(nextByte)
            elif (current_modifier == RegExModifiers.NONE):
                    self._valid == False
                    nextByteValid = False
        elif (type(current_requirement) is RegExPattern):
            if (self.subpattern_matcher == None):
                self.subpattern_matcher = RegExMatcher(current_requirement, self.start_index + self.length)
            if (self.subpattern_matcher.isDone()):
                if (current_modifier == RegExModifiers.STAR):
                    self.subpattern_matcher._reset()
                elif (current_modifier == RegExModifiers.QMARK or current_modifier == RegExModifiers.NONE):
                    self._advance()
                    self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
                    self.subpattern_matcher = None
                
                self.validate(nextByte)
            elif (not self.subpattern_matcher.validate(nextByte)):
                if (current_modifier == RegExModifiers.STAR or current_modifier == RegExModifiers.QMARK):
                    self._advance()
                    self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
                    self.subpattern_matcher = None
                    self.validate(nextByte)
                elif (current_modifier == RegExModifiers.NONE):
                    self._valid == False
                    nextByteValid = False
            
        return nextByteValid


if __name__ == "__main__":
    i = 0
    initiators = {"AA" :  [RegExPattern("(AA)+", "lol")]}
    m = []
    s = "AAAAAABBAAAA"
    while i < len(s):
        if (s[i:i+2] in initiators.keys()):
            for pattern in initiators[s[i:i+2]]:
                m.append(RegExMatcher(pattern,i))
        print(i,s[i:i+2], m)

        toDelete = []
        for matcher in m:
            matcher.validate(s[i:i+2])
            if (not matcher.isValid()):
                toDelete.append(matcher)
            elif (matcher.isDone()):
                print("DONE! ", matcher.start_index, matcher.length)
                toDelete.append(matcher)

        for bruh in toDelete:
            m.remove(bruh)

        
        i += 2

    toDelete = []
    for matcher in m:
        if (not matcher.isValid()):
            toDelete.append(matcher)
        elif (matcher.isDone(cleanup=True)):
            print("DONE! ", matcher.start_index, matcher.length)
            toDelete.append(matcher)

    for bruh in toDelete:
        m.remove(bruh)