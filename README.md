# binary-regex-parser


A program tto find regex patttterns in binary files.

## Usage

### Binary RegEx Expressions
The RegEx are binary and in Hexadecimal, this means tthat charactes come in groups of two.

For Example:
    Unlike in regular RegEx, in the pattern "AA+" tthe "+" character relates to the preceding "AA".

All Regex expressions passed as arguments to the program must be in that format.

#### Supported Modifiers
- `XX?` - `XX` doesn't have tto appear, butt can appear once  
- `XX*` - Matches at least 0 repetitions of `XX`
- `XX*` - Matches at least 1 repetition of `XX` 
- `XX{a}` - Matches exactly `a` occurrences of `XX` 
- `XX{a,b}` - Matches between `a` and `b` occurrences of `XX`
- `.` - Matches any byte
- `[]` - Capture group
  - `[XXYY]` - next byte can be either `XX` or `YY`
  - `[XX-YY]` - next byte can be antything between `XX` and `YY`
  - `[ZZXX-YY]` - next byte can be antything between `XX` and `YY`, or it can be `ZZ`
  - `[^XX]` - negated set, acceptts all possible values but those in the set (here every byte but `XX` will be acceptted)
- `()` - Sub-pattern, a nestted regex patttern. Modifiers after this pattern relate to the entire sub-pattern.

### Output Format
The output format is a list of objects.

Each object represents one occurence of a regular expression in the format:
```JSON
{
    "length": "int",
    "name": "string",
    "indices": {
        "start": "int",
        "end": "int"
    }
}
```
