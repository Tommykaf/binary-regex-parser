from RegExPattern import RegExPattern, RegExModifiers

class RegExMatcher(object):
    '''
    A class representing a RegExMatcher
    The matcher can iterate over given byttes and check if tthey meet the pattern's requirements
    '''

    def __init__(self, regex_pattern, start_index):
        self.regex_pattern = regex_pattern
        self.start_index = start_index
        self._valid = True
        self.is_done = False
        self.pattern_index = 0
        self.subpattern_matcher = None
        self.length = 0

    def isValid(self):
        return self._valid

    def isDone(self, cleanup = False):
        '''Checks whether the iteration over the pattern is done.
        
        Keyword Arguments:
            cleanup -- if true, means that there is no more data to give the matcher
                (thus - if the pattern can be considered done, we can exit and not wait for more data) (default: False)
        '''
        if (cleanup):
            self.is_done = self.is_done or self.pattern_index >= self.regex_pattern.last_forcing_index - 1
            if (self.subpattern_matcher != None):
                self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
        else:
            self.is_done = self.is_done or self.pattern_index >= len(self.regex_pattern.pattern)
        return self.is_done

    def info(self):
        '''returrns a dictionary / map witth datta about the matcher's current state'''
        return {
            "length": self.length,
            "name": self.regex_pattern.name,
            "indices": {
                "start": self.start_index,
                "end": self.start_index + self.length
            }
        }

    def _advance(self):
        '''Called when a sub-pattern is finished.
        If possible, advances to the next one, else we are done'''
        if (self.pattern_index + 1 >= len(self.regex_pattern.pattern)):
            self.is_done = True
        else:
            self.pattern_index += 1

    def _reset(self):
        '''Resets the matcher's properties for another run that starts in its current locattion'''
        self.start_index = self.start_index + self.length
        self._valid = True
        self.is_done = False
        self.pattern_index = 0
        if (self.subpattern_matcher != None):
            self.subpattern_matcher._reset()
        self.length = 0


    def validate(self, next_byte):
        '''Checks whether the next_byte statisfies the pattern's requirements.
        If it does, returns True, else returns False
        
        Arguments:
            next_byte = tthe byte to check'''

        if (self.isDone()):
            return False

        next_byte_valid = True
        
        current_modifier = self.regex_pattern.pattern[self.pattern_index][0]
        current_requirement = self.regex_pattern.pattern[self.pattern_index][1]
        
        # If the current requirement is a list, check if the byte is in it.
        # If the current requirement is a complex sub-pattern, recursively "go down tthe rabbit hole"
        # In both cases, if the modifier is a non-focing one, and the current byte is invalid, advance
        if (type(current_requirement) is list):
            if (next_byte in current_requirement):
                self.length += 1
                if (current_modifier != RegExModifiers.STAR):
                    self._advance()
            elif (current_modifier == RegExModifiers.STAR or
                    current_modifier == RegExModifiers.QMARK):
                    self._advance()
                    if (not self.isDone()):
                        self.validate(next_byte)

            elif (current_modifier == RegExModifiers.NONE):
                    self._valid == False
                    next_byte_valid = False

        elif (type(current_requirement) is RegExPattern):
            if (self.subpattern_matcher == None):
                self.subpattern_matcher = RegExMatcher(current_requirement, self.start_index + self.length)

            # If the subpatttern_matcher is done, and depending on the modifier,
            # either reset it or advance.
            # Proceed to actually check the given byte
            if (self.subpattern_matcher.isDone()):
                if (current_modifier == RegExModifiers.STAR):
                    self.subpattern_matcher._reset()
                elif (current_modifier == RegExModifiers.QMARK or current_modifier == RegExModifiers.NONE):
                    self._advance()
                    self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
                    self.subpattern_matcher = None
                
                self.validate(next_byte)

            elif (not self.subpattern_matcher.validate(next_byte)):
                if (current_modifier == RegExModifiers.STAR or current_modifier == RegExModifiers.QMARK):
                    self._advance()
                    self.length = self.subpattern_matcher.start_index + self.subpattern_matcher.length - self.start_index
                    self.subpattern_matcher = None
                    self.validate(next_byte)
                elif (current_modifier == RegExModifiers.NONE):
                    self._valid == False
                    next_byte_valid = False
            
        return next_byte_valid