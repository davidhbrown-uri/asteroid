#########################################################################
# A tree walker to interpret Asteroid programs
#
# (c) 2018 - Lutz Hamel, University of Rhode Island
#########################################################################

from asteroid_state import state
from asteroid_support import assert_match
from asteroid_support import unify
from asteroid_support import promote
from pprint import pprint

__retval__ = None  # return value register for escaped code

#########################################################################
# Use the exception mechanism to return values from function calls

class ReturnValue(Exception):
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return(repr(self.value))

#########################################################################
def len_seq(seq_list):

    if seq_list[0] == 'nil':
        return 0

    elif seq_list[0] == 'seq':
        # unpack the seq node
        (SEQ, p1, p2) = seq_list

        return 1 + len_seq(p2)

    else:
            raise ValueError("unknown node type: {}".format(seq_list[0]))

#########################################################################
def eval_actual_args(args):

    return walk(args)

#########################################################################
def declare_formal_args(unifiers):
    # unfiers is of the format: [ (sym, term), (sym, term),...]

    for u in unifiers:
        sym, term = u
        state.symbol_table.enter_sym(sym, term)

#########################################################################
def handle_call(fval, actual_arglist):
    
    if fval[0] != 'function':
        raise ValueError("handle_call: not a function")

    actual_val_args = eval_actual_args(actual_arglist)   # evaluate actuals in current symtab
    body_list = fval[1]   # get the list of function bodies - nil terminated seq list

    # iterate over the bodies to find one that unifies with the actual parameters
    (BODY_LIST, body_list_ix) = body_list
    unified = False

    while body_list_ix[0] != 'nil':
        (SEQ, body, next) = body_list_ix

        (BODY, 
         (PATTERN, p),
         (STMT_LIST, stmts)) = body

        try:
            unifiers = unify(actual_val_args, p)
            unified = True
        except:
            unifiers = []
            unified = False

        if unified:
            break
        else:
            body_list_ix = next

    if not unified:
        ValueError("handle_call: none of the function bodies unified with actual parameters")

    # dynamic scoping for functions!!!
    state.symbol_table.push_scope()
    declare_formal_args(unifiers)

    # execute the function
    try:
        walk(stmts)         
    except ReturnValue as val:
        return_value = val.value
    else:
        return_value = ('none',) # need that in case function has no return statement

    # return to the original scope
    state.symbol_table.pop_scope()

    return return_value

#########################################################################
# node functions
#########################################################################
def attach_stmt(node):

    (ATTACH, f, (CONSTR_ID, sym)) = node
    assert_match(ATTACH, 'attach')
    assert_match(CONSTR_ID, 'constr-id')

    if f[0] == 'fun-id':
        fval = state.symbol_table.lookup_sym(f[1])
    elif f[0] == 'fun-const':
        fval = f[1]

    if fval[0] != 'function':
        raise ValueError("{} is not a function".format(f[1]))
    else:
        state.symbol_table.attach_to_sym(sym, fval)

#########################################################################
def assign_stmt(node):

    (ASSIGN, pattern, exp) = node
    assert_match(ASSIGN, 'assign')
    
    term = walk(exp)
    unifiers = unify(term, pattern)

    # TODO: check for repeated names in the unfiers

    for unifier in unifiers:
        name, value = unifier
        state.symbol_table.enter_sym(name, value)

#########################################################################
def get_stmt(node):

    (GET, name) = node
    assert_match(GET, 'get')

    s = input("Value for " + name + '? ')
    
    try:
        value = int(s)
    except ValueError:
        raise ValueError("expected an integer value for " + name)
    
    state.symbol_table.update_sym(name, ('scalar', value))

#########################################################################
def print_stmt(node):

    # TODO: deal with files and structures/lists

    (PRINT, exp, f) = node
    assert_match(PRINT, 'print')
    
    value = walk(exp)
    print("{}".format(value))

#########################################################################
def call_stmt(node):

    (CALLSTMT, name, actual_args) = node
    assert_match(CALLSTMT, 'callstmt')

    handle_call(name, actual_args)

#########################################################################
def return_stmt(node):

    (RETURN, e) = node
    assert_match(RETURN, 'return')

    if e[0] == 'nil': # no return value
        raise ReturnValue(('none',))

    else:
        raise ReturnValue(walk(e))

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'while')
    
    value = walk(cond)
    while value != 0:
        walk(body)
        value = walk(cond)

#########################################################################
def if_stmt(node):
    
    try: # try the if-then pattern
        (IF, cond, then_stmt, (NIL,)) = node
        assert_match(IF, 'if')
        assert_match(NIL, 'nil')

    except ValueError: # if-then pattern didn't match
        (IF, cond, then_stmt, else_stmt) = node
        assert_match(IF, 'if')
        
        value = walk(cond)
        
        if value != 0:
            walk(then_stmt)
        else:
            walk(else_stmt)

    else: # if-then pattern matched
        value = walk(cond)
        if value != 0:
            walk(then_stmt)

#########################################################################
def block_stmt(node):
    
    (BLOCK, stmt_list) = node
    assert_match(BLOCK, 'block')
    
    state.symbol_table.push_scope()
    walk(stmt_list)
    state.symbol_table.pop_scope()

#########################################################################
def plus_exp(node):
    
    (PLUS,c1,c2) = node
    assert_match(PLUS, '__plus__')
    
    v1 = walk(c1)
    v2 = walk(c2)

    fval = state.symbol_table.lookup_sym('__plus__')
    
    if fval[0] == 'constructor':
        return ('__plus__', v1, v2)

    elif fval[0] == 'function':
        arglist = ('list', [v1, v2])
        v = walk(('juxta',
                  fval,
                  ('juxta',
                   arglist,
                   ('nil',))))
        return v

    else:
        raise ValueError("{} not implemented in __plus__".format(fval[0]))

#########################################################################
def minus_exp(node):
    
    (MINUS,c1,c2) = node
    assert_match(MINUS, '-')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 - v2

#########################################################################
def times_exp(node):
    
    (TIMES,c1,c2) = node
    assert_match(TIMES, '*')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 * v2

#########################################################################
def divide_exp(node):
    
    (DIVIDE,c1,c2) = node
    assert_match(DIVIDE, '/')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return v1 // v2

#########################################################################
def eq_exp(node):
    
    (EQ,c1,c2) = node
    assert_match(EQ, '==')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return 1 if v1 == v2 else 0

#########################################################################
def le_exp(node):
    
    (LE,c1,c2) = node
    assert_match(LE, '<=')
    
    v1 = walk(c1)
    v2 = walk(c2)
    
    return 1 if v1 <= v2 else 0

#########################################################################
def juxta_exp(node):
    # could be a call: fval fargs
    # could be a list access: x [0]

    (JUXTA, val, args) = node
    assert_match(JUXTA, 'juxta')

    if args[0] == 'nil':
        return val

    v = walk(val)

    if v[0] == 'function': # execute a function call
        # if it is a function vall then the args node is another
        # 'juxta' node
        (JUXTA, parms, rest) = args
        assert_match(JUXTA, 'juxta')
        return walk(('juxta', handle_call(v, parms), rest))

    else: # not yet implemented
        raise ValueError("'juxta' not implemented for {}".format(v[0]))

#########################################################################
def uminus_exp(node):
    
    (UMINUS, exp) = node
    assert_match(UMINUS, 'uminus')
    
    val = walk(exp)
    return - val

#########################################################################
def not_exp(node):
    
    (NOT, exp) = node
    assert_match(NOT, 'not')
    
    val = walk(exp)
    return 0 if val != 0 else 1

#########################################################################
def list_exp(node):

    (LIST, inlist) = node
    assert_match(LIST, 'list')

    outlist =[]

    for e in inlist:
        outlist.append(walk(e))

    return ('list', outlist)

#########################################################################
def escape_exp(node):

    (ESCAPE, s) = node
    assert_match(ESCAPE, 'escape')

    global __retval__
    __retval__ = ('none',)

    exec(s)

    return __retval__

#########################################################################
# walk
#########################################################################
def walk(node):
    # node format: (TYPE, [child1[, child2[, ...]]])
    type = node[0]
    
    if type in dispatch_dict:
        node_function = dispatch_dict[type]
        return node_function(node)
    else:
        raise ValueError("walk: unknown tree node type: " + type)

# a dictionary to associate tree nodes with node functions
dispatch_dict = {
    # statements
    'attach'  : attach_stmt,
    'assign'  : assign_stmt,
    'get'     : get_stmt,
    'print'   : print_stmt,
    'callstmt': call_stmt,
    'return'  : return_stmt,
    'while'   : while_stmt,
    'if'      : if_stmt,
    'block'   : block_stmt,

    # expressions
    'list'    : list_exp,
    'seq'     : lambda node : ('seq', walk(node[1]), walk(node[2])),
    'nil'     : lambda node : node,
    'function': lambda node : node, # looks like a constant
    'string'  : lambda node : node,
    'integer' : lambda node : node,
    'real'    : lambda node : node,
    'id'      : lambda node : state.symbol_table.lookup_sym(node[1]),
    'juxta'   : juxta_exp,
    'escape'  : escape_exp,

    # built-in operators
    '__plus__'    : plus_exp,
    '__minus__'   : minus_exp,
    '*'       : times_exp,
    '/'       : divide_exp,
    '=='      : eq_exp,
    '<='      : le_exp,
    'uminus'  : uminus_exp,
    'not'     : not_exp
}


