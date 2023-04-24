###########################################################################################
# globals for Asteroid
#
# (c) University of Rhode Island
###########################################################################################

from asteroid.support import term2string #Used by redundantPatternFound exception

###########################################################################################
# this is used to compute the filename extensions of the modules
asteroid_file_suffix = ".ast"

###########################################################################################
# symbols for builtin operators.
# NOTE: if you add new builtins make sure to keep this table in sync.

binary_operators = {
    '__plus__',
    '__minus__',
    '__times__',
    '__divide__',
    '__or__',
    '__and__',
    '__eq__',
    '__ne__',
    '__le__',
    '__lt__',
    '__ge__',
    '__gt__',
    }

unary_operators = {
    '__uminus__',
    '__uplus__',
    '__not__',
    }

operator_symbols = binary_operators | unary_operators

#########################################################################
# Use the exception mechanism to return values from function calls

class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))

#########################################################################
class Break(Exception):

    def __str__(self):
        return("break statement exception")

#########################################################################
# exception generated by the throw statement

class ThrowValue(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(str(self.value))

#########################################################################
class PatternMatchFailed(Exception):
    def __init__(self, value):
        self.value = "pattern match failed: " + value

    def __str__(self):
        return(self.value)

#########################################################################
class NonLinearPatternError(Exception):
    def __init__(self, value):
        self.value = "non-linear pattern error: " + value

    def __str__(self):
        return(self.value)

#########################################################################
class ExpectationError(Exception):
    def __init__(self, found, expected):
        self.found_EOF = (found == 'EOF')
        self.value = "expected {} found {}.".format(str(expected), str(found))

    def __str__(self):
        return(self.value)
        
##############################################################################################
# *** Part of the Redundant Pattern Detector ***
#
# This exception is used when a pattern has been identified as being 'useless',
# or reundant. This exception is formatted to pack both offending patterns
# information into a single formatted message to the user informing them of
# where and what caused this error.
##############################################################################################
class RedundantPatternFound(Exception):
    """Exception raised for detection of redundant pattern in function declaration.
    Attributes:
        pattern1 -- The pattern with the higher order of precedence (comparer).
        line1    -- The line number location of pattern 1 in its file.
        pattern2 -- The pattern with the lower order of precedence  (comparee).
        line2    -- The line number location of pattern 2 in its file.
        function -- The name of the function where the redundancy was found.
        file     -- The name of the file where the function is from.
    """
    def __init__(self, pattern1, pattern2,function_name,location1,location2):

        self.pattern1 = pattern1
        self.line1 = str(location1[1] - 1) #patterns dont have line #, so we
                                            #compensate here by using the first line
                                            # of the patterns body, then moving back
                                            # 1 line(minus 1)
        self.pattern2 = pattern2
        if (location2 != None):
            self.line2 = str(location2[1] - 1)
        if (location1 != None):
            self.file = location1[0]
        self.function = function_name
        self.message = "redundant pattern detected in '{}': ".format(self.function)
        self.message += "the pattern on line {} will consume all matches for pattern on line {}"\
                            .format(self.line1,self.line2)
        super().__init__(self.message)

    def __str__(self):
        return(self.message)

###########################################################################################
# expression nodes not allowed in terms or patterns for unification. these are all nodes
# that express some sort of computation

unify_not_allowed = {
    'function-val',
    'to-list',
    'where-list',
    'raw-to-list',
    'raw-where-list',
    'foreign',
    'escape',
    'is',
    'in',
}

###########################################################################################
# list of structures that constitute patterns

patterns = {
    'pattern',
    'id',
    'string',
    'real',
    'integer',
    'list',
    'tuple',
    'boolean',
    'none',
    'object',
    'struct',
    'typematch',
}

###########################################################################################
# list of structures that a pattern type-pattern will subsume/overlap

pattern_subsumes = patterns - {'id'}

###########################################################################################
# the debugger object set by the interpreter at start time
debugger = None

def set_debugger(dbg):
    debugger = dbg

