#!/usr/bin/env python
import sys
#import time
import argparse
from Core_DPLL_Algorithm import parse_dimacs, cdcl

def main():
    
    # Set options to disable 'watched literals' or choosing own output file name.
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='CNF file in DIMACS format')
    parser.add_argument('--no-watched', action='store_true', help='Disable watched literals')
    args = parser.parse_args()

    #### ask to input the cnf file name, parse the cnf file.
    clauses, num_vars = parse_dimacs(args.input)
    
    # Diable or enable run time tracking.
    #start = time.time()
    sat, model = cdcl(clauses, num_vars, use_watched=not args.no_watched)
    #end = time.time()


    # Publish result - SAT or UNSAT.
    if sat:
        print("RESULT:SAT")
        assign = {i: 0 for i in range(1, num_vars+1)}
        for lit in model:
            assign[abs(lit)] = 1 if lit > 0 else 0
        print("ASSIGNMENT:" + " ".join(f"{i}={assign[i]}" for i in range(1, num_vars+1)))
    else:
        print("RESULT:UNSAT")

    #print(f"Time taken: {end-start:.4f} seconds")

if __name__ == "__main__":
    main()
