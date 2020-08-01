from RegExPattern import RegExPattern
from RegExMatcher import RegExMatcher

def read_from_file(path, readbuffer = 2**20, buffer = 2**13):
    with open(path, "rb") as fl:
        for chunk in iter(lambda: fl.read(readbuffer), ''):
            while chunk != '':
                yield chunk[:buffer]
                chunk = chunk[buffer:]
            

def main(path, regex_map, readbuffer = 2**20, buffer = 2**13):

    res = []
    fl = read_from_file(path, readbuffer, buffer)

    #initialize map from first byte to regexs that it can start with
    initiator_map = {}
    for regex, name in regex_map.items():
        pattern = RegExPattern(regex,name)
        for initiator in pattern.initiators:
            if not initiator_map.get(initiator, False):
                initiator_map[initiator] = []
            initiator_map[initiator].append(pattern)
    
    
    current_patterns = []
    current_matchers = []
    buffer = ''
    buffer = next(fl, None)
    while buffer != b'':
        i = 0
        while i < len(buffer):
            current_byte = int(buffer[i:i+2],16)
            if (current_byte in initiator_map.keys()):
                for pattern in initiator_map[current_byte]:
                    if pattern not in current_patterns:
                        current_patterns.append(pattern)
                        current_matchers.append(RegExMatcher(pattern,i))

            toDelete = []
            for matcher in current_matchers:
                matcher.validate(current_byte)
                if (not matcher.isValid()):
                    toDelete.append(matcher)
                elif (matcher.isDone()):
                    res.append(matcher.info())
                    toDelete.append(matcher)

            for matcher in toDelete:
                current_matchers.remove(matcher)
                current_patterns.remove(matcher.regex_pattern)
            
        
            i += 2
        buffer = next(fl)
    
    toDelete = []
    for matcher in current_matchers:
        if (not matcher.isValid()):
            toDelete.append(matcher)
        elif (matcher.isDone(cleanup=True)):
            res.append(matcher.info())
            toDelete.append(matcher)

    for bruh in toDelete:
        current_matchers.remove(bruh)
        current_patterns.remove(matcher.regex_pattern)

    return res

    


if __name__ == "__main__":
    print(main("./test1.bin", {"AA":"aa","AA+":"AA+","BB":"BB"}))