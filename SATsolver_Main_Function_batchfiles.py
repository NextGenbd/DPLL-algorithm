# mySAT.py (runner with batch mode)
#!/usr/bin/env python3
import os
import glob
import time
import argparse
from Core_DPLL_Algorithm import parse_dimacs, cdcl

def main():
    
    # Set options to disable 'watched literals' or choosing own output file name.
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', help='File or folder paths to CNF files')
    parser.add_argument('--no-watched', action='store_true', help='Disable watched literals')
    parser.add_argument('--output', default='batch_results.txt', help='Output file for results')
    args = parser.parse_args()

    # ask to input the cnf file name, parse the cnf file, then run the DPLL...
    # algorithm--> publish result at the end
    results = []
    for path in args.paths:
        if os.path.isdir(path):
            cnf_files = glob.glob(os.path.join(path, '*.cnf'))
            output_path_name = path + '_output'
            for cnf in cnf_files:
                start = time.time()
                clauses, num_vars = parse_dimacs(cnf)
                sat, model = cdcl(clauses, num_vars, use_watched=not args.no_watched)
                elapsed = time.time() - start
                assign_str = ''
                if sat:
                    assign = {i:0 for i in range(1, num_vars+1)}
                    for lit in model: assign[abs(lit)] = 1 if lit>0 else 0
                    assign_str = 'ASSIGNMENT:' + ' '.join(f"{i}={assign[i]}" for i in range(1, num_vars+1))
                results.append(f"{os.path.basename(output_path_name)}/{os.path.basename(cnf)}: RESULT:{'SAT' if sat else 'UNSAT'} {assign_str} Time: {elapsed:.4f}s")
        elif os.path.isfile(path) and path.endswith('.cnf'):
            start = time.time()
            clauses, num_vars = parse_dimacs(path)
            sat, model = cdcl(clauses, num_vars, use_watched=not args.no_watched)
            elapsed = time.time() - start
            assign_str = ''
            if sat:
                output_path_name = path + '_output'
                assign = {i:0 for i in range(1, num_vars+1)}
                for lit in model: assign[abs(lit)] = 1 if lit>0 else 0
                assign_str = 'ASSIGNMENT:' + ' '.join(f"{i}={assign[i]}" for i in range(1, num_vars+1))
            results.append(f"{os.path.basename(output_path_name)}: RESULT:{'SAT' if sat else 'UNSAT'} {assign_str} Time: {elapsed:.4f}s")

    with open(args.output, 'w') as fout:
        fout.write('\n'.join(results))

    print(f"Results written to {args.output}")

if __name__ == '__main__':
    main()
