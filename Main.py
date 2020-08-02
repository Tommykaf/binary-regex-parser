from RegExPattern import RegExPattern
from RegExMatcher import RegExMatcher
import argparse
import json

def read_from_file(path, readbuffer = 2**20, buffer_size = 2**13):
    '''
    A generator used for buffered reading from a file
    
    Arguments:
        path - path to a binary file object open for reading (open(path,"rb"))
        readbuffer - a buffer for reading from io - should be bigger than buffer
        buffer - the size of the buffer yielded by the generator
    '''
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
    '''
    Find regex expressions in a binary file.
    
    Arguments:
        path - path to a binary file object open for reading (open(path,"rb"))
        regex_map - a map with binary regex expressions as keys and their names as values
        readbuffer - a buffer for reading from io - should be bigger than buffer
        buffer - the size of the buffer yielded by the generator
    
    Returns:
        A list of dictionaries of the following scheme:
            {
                length: int,
                name: string,
                indices: {
                    start: int,
                    end: int
                }
            }
            Each dicttionary represents one occurence of a regex expression
    '''

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

    
def initialize_parser():
    parser = argparse.ArgumentParser(description='''A program for matching regex expressions in binary files. Usage example:
            python .\Main.py .\\file_path '{\\\"patttern1\\\": \\\"patttern1_name\\\",\\\"patttern2\\\": \\\"patttern2_name\\\"}' --readbuffer 8192 --buffer 1024''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', metavar='FILENAME',
                   help='a path to an input file')
    parser.add_argument('map', metavar='REGEX_MAP', type=json.loads,
                   help='a map of scheme {{"binary-regex":"regex_name"}}')

    parser.add_argument('--readbuffer', type=int, default=2**20,
                   help='num of bytes read from tthe file each iteration')

    parser.add_argument('--output', default=None,
                   help='file to output to')

    parser.add_argument('--buffer', type=int, default=2**13,
                   help='num of bytes processed each iteration')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = initialize_parser()
    res = main(args.file,args.map,args.readbuffer,args.buffer)
    if args.output == None:
        print(res)
    else:
        output_file = open(args.output,"w")
        output_file.write(str(res))
        output_file.flush()
        output_file.close()
   