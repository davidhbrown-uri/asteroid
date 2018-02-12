#!/usr/bin/env python
###########################################################################################
# Asteroid interpreter
#
# (c) 2018 - Lutz Hamel, University of Rhode Island
###########################################################################################

from argparse import ArgumentParser
from asteroid_gram import Parser
from asteroid_state import state
from asteroid_interp_walk import walk
from asteroid_support import dump_AST

# TODO: adjust the defaults
def interp(input_stream, tree_dump=True, do_walk=True, symtab_dump=True, exceptions=False):

    # initialize the state object
    state.initialize()

    # populate the symbol table with predefined behavior for operators - constructors!
    state.symbol_table.enter_sym('__plus__', ('constructor', ('arity', 2)))
    state.symbol_table.enter_sym('__minus__', ('constructor', ('arity', 2)))

    # build the AST
    parser = Parser()
    state.AST = parser.parse(input_stream)

    try:
        # walk the AST
        if tree_dump:
            dump_AST(state.AST)
        if do_walk:
            walk(state.AST)
        if symtab_dump:
            state.symbol_table.dump()
    except Exception as e:
        if exceptions: # rethrow the exception so that you can see it
            raise e
        else:
            print("Error: {}".format(e))

if __name__ == "__main__":
    # parse command line args
    aparser = ArgumentParser()
    aparser.add_argument('-t','--tree', action='store_true', help='AST dump flag')
    aparser.add_argument('-w','--no_walk', action='store_false', help='walk flag')
    aparser.add_argument('-s','--symtab', action='store_true', help='symbol table dump flag')
    aparser.add_argument('input', metavar='input_file', help='Asteroid input file')

    args = vars(aparser.parse_args())

    f = open(args['input'], 'r')
    input_stream = f.read()
    f.close()

    # execute interpreter
    interp(input_stream=input_stream, 
           tree_dump=args['t'],
           do_walk=args['w'],
           symtab_dump=args['s'])
