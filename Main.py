from RegExPattern import RegExPattern
from RegExMatcher import RegExMatcher

def read_from_file(path, readbuffer = 2**20, buffer_size = 2**13):
    with open(path, "rb") as fl:
        for chunk in iter(lambda: fl.read(readbuffer), b''):
            while chunk != b'':
                if len(chunk) > buffer_size:
                    yield chunk[:buffer_size]
                    chunk = chunk[buffer_size:]
                else:
                    yield chunk
                    chunk = b''

            

def main(path, regex_map, readbuffer = 2**20, buffer_size = 2**13):

    res = []
    fl = read_from_file(path, readbuffer, buffer_size)

    #initialize map from bytes to regexs that can start with it
    initiator_map = {}
    for regex, name in regex_map.items():
        pattern = RegExPattern(regex,name)
        for initiator in pattern.initiators:
            if not initiator_map.get(initiator, False):
                initiator_map[initiator] = []

            initiator_map[initiator].append(pattern)
    
    
    current_patterns = []
    current_matchers = []
    buffer = next(fl, b'')
    bufferNum = 0
    while buffer != b'':
        i = 0
        while i < len(buffer):
            current_byte = buffer[i]

            # Check whteher matchers can be initiatted.
            # No ttwo pattterns of tthe same kind can overlap.
            if (current_byte in initiator_map.keys()):
                for pattern in initiator_map[current_byte]:
                    if pattern not in current_patterns:
                        current_patterns.append(pattern)
                        current_matchers.append(RegExMatcher(pattern, bufferNum * buffer_size + i))

            # If a matcher is eitther done or invalid, it should be deleted
            # along with it's pattern.
            # If it is done, append it's info to res.
            toDelete = []
            for matcher in current_matchers:
                if (not matcher.validate(current_byte) or not matcher.isValid()):
                    toDelete.append(matcher)
                elif (matcher.isDone()):
                    res.append(matcher.info())
                    toDelete.append(matcher)

            # Maintenance check, delete all that we can
            # in addittion, initiate matchers for patterns that have just now failed 
            for matcher in toDelete:
                current_matchers.remove(matcher)
                current_patterns.remove(matcher.regex_pattern)
                
                if (not matcher.isValid() and 
                    current_byte in initiator_map.keys() and
                    matcher.regex_pattern in initiator_map[current_byte]):

                    current_patterns.append(matcher.regex_pattern)
                    restartMatcher = RegExMatcher(matcher.regex_pattern, bufferNum * buffer_size + i)
                    current_matchers.append(restartMatcher)
                    restartMatcher.validate(current_byte)
            
        
            i += 1
        bufferNum += 1
        try:
            buffer = next(fl)
        except StopIteration as e:
            break
    
    # Final Cleanup
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
    print(main("./flame-qd1a.190821.007/bootloader-flame-c2f2-0.2-5799621.img", { '5D00008000': 'lzma',
  '27051956': 'uImage',
  '18286F01': 'zImage',
  '1F8B0800': 'gzip',
  '303730373031': 'cpio',
  '303730373032': 'cpio',
  '303730373033': 'cpio',
  '894C5A4F000D0A1A0A': 'lzo',
  '5D00000004': 'lzma',
  'FD377A585A00': 'xz',
  '314159265359': 'bzip2',
  '425A6839314159265359': 'bzip2',
  '04224D18': 'lz4',
  '02214C18': 'lz4',
  '1F9E08': 'gzip',
  '71736873': 'squashfs',
  '68737173': 'squashfs',
  '51434454': 'dtb',
  'D00DFEED': 'fit',
  '7F454C46': 'elf',
  "4642504B0100+": "START",
  "525C":"525C",
  "[4642504B0100]+": "START++",
  "4642504B0100{1,3}": "START++"}))