###########################################################################################
# globals for Asteroid
#
# (c) Lutz Hamel, University of Rhode Island
###########################################################################################

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
        return(repr(self.value))

#########################################################################
class PatternMatchFailed(Exception):
    def __init__(self, value):
        self.value = "pattern match failed: " + value

    def __str__(self):
        return(repr(self.value))

###########################################################################################
# expression nodes not allowed in terms or patterns for unification. these are all nodes
# that express some sort of computation

unify_not_allowed = {
    'function-val',
    'to-list',
    'where-list',
    'raw-to-list',
    'raw-where-list',
    'if-exp',
    'foreign',
    'escape',
    'is',
    'in',
    'otherwise',
}

###########################################################################################
