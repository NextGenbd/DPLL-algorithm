########## DPLL-algorithm############
### To run single files:
compile : SATsolver_Main_Function.py
It uses the source code: Core_DPLL_Algorithm.py
format: python3 SATsolver_Main_Function.py cnf_file_name.cnf
example : python3 SATsolver_Main_Function.py uf20-01.cnf
# To run without watched literals: python3 SATsolver_Main_Function.py  uf20-01.cnf --no-watched

### To run batch files:
compile : SATsolver_Main_Function_batchfiles.py
It uses the source code: Core_DPLL_Algorithm.py
format: python3 SATsolver_Main_Function_batchfiles.py  folder_name output=outut_file_name.txt
example : python3 SATsolver_Main_Function_batchfiles.py Selected_Problems output=Selected_Problems.txt

### To do timign analysis: enable the following lines in the file: 
File:             SATsolver_Main_Function.py
line 3: import time

line 18: Diable or enable run time tracking.
line 19: start = time.time()
line 21: end = time.time()
Line 34: print(f"Time taken: {end-start:.4f} seconds")
