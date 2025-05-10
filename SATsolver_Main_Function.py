# Core_DPLL_Algorithm.py (with watched literal propagation logic and conflict limit)

from collections import deque

class Clause:
    def __init__(self, literals, use_watched):
        self.literals = literals
        self.size = len(literals)
        self.use_watched = use_watched
        if use_watched:
            if self.size >= 2:
                self.w1, self.w2 = 0, 1
            elif self.size == 1:
                self.w1 = self.w2 = 0
        else:
            self.w1 = self.w2 = None

    def is_satisfied(self, assignment):
        return any((assignment.get(abs(l), 0) == (1 if l > 0 else -1)) for l in self.literals)

    def is_conflict(self, assignment):
        return all((assignment.get(abs(l), 0) != (1 if l > 0 else -1)) for l in self.literals)

    def unit_literal(self, assignment):
        unassigned = [l for l in self.literals if assignment.get(abs(l), 0) == 0]
        if any((assignment.get(abs(l), 0) == (1 if l > 0 else -1)) for l in self.literals):
            return None
        return unassigned[0] if len(unassigned) == 1 else None

class CNFFormula:
    def __init__(self, clauses, num_vars, use_watched=True):
        self.num_vars = num_vars
        self.assignment = {i: 0 for i in range(1, num_vars + 1)}
        self.decision_level = {i: 0 for i in range(1, num_vars + 1)}
        self.antecedent = {i: None for i in range(1, num_vars + 1)}
        self.stack = []
        self.use_watched = use_watched
        self.clauses = [Clause(c, use_watched) for c in clauses]

        if use_watched:
            self.watched = {i: [] for i in range(-num_vars, num_vars + 1) if i != 0}
            for cl in self.clauses:
                self.watched[cl.literals[cl.w1]].append(cl)
                if cl.w2 is not None and cl.w2 < cl.size:
                    self.watched[cl.literals[cl.w2]].append(cl)

    def all_assigned(self):
        return all(v != 0 for v in self.assignment.values())

    def enqueue(self, lit, level, ante=None):
        var = abs(lit)
        self.assignment[var] = 1 if lit > 0 else -1
        self.decision_level[var] = level
        self.antecedent[var] = ante
        self.stack.append((lit, level))

    def backtrack(self, level):
        while self.stack and self.stack[-1][1] > level:
            lit, _ = self.stack.pop()
            var = abs(lit)
            self.assignment[var] = 0
            self.antecedent[var] = None
            self.decision_level[var] = 0

    def unit_propagation(self, level):
        if not self.use_watched:
            queue = deque()
            for cl in self.clauses:
                ul = cl.unit_literal(self.assignment)
                if ul is not None:
                    queue.append((cl, ul))
            while queue:
                cl, lit = queue.popleft()
                var = abs(lit)
                val = self.assignment[var]
                if val != 0 and val != (1 if lit > 0 else -1):
                    return cl
                if val == 0:
                    self.enqueue(lit, level, cl)
                    for c in self.clauses:
                        if c.is_satisfied(self.assignment): continue
                        ul2 = c.unit_literal(self.assignment)
                        if ul2 is not None:
                            queue.append((c, ul2))
                        elif c.is_conflict(self.assignment):
                            return c
            return None
        else:
            queue = deque([lit for var, val in self.assignment.items() if val != 0 for lit in [-var if val == 1 else var]])
            while queue:
                false_lit = queue.popleft()
                watching = list(self.watched.get(false_lit, []))
                for cl in watching:
                    if cl.literals[cl.w1] == false_lit:
                        i, j = cl.w1, cl.w2
                    else:
                        i, j = cl.w2, cl.w1
                    found_new_watch = False
                    for k in range(cl.size):
                        if k != i and self.assignment.get(abs(cl.literals[k]), 0) != -(1 if cl.literals[k] > 0 else -1):
                            cl.w1, cl.w2 = j, k
                            self.watched[false_lit].remove(cl)
                            self.watched[cl.literals[k]].append(cl)
                            found_new_watch = True
                            break
                    if not found_new_watch:
                        val_j = self.assignment.get(abs(cl.literals[j]), 0)
                        if val_j == 0:
                            self.enqueue(cl.literals[j], level, cl)
                            queue.append(cl.literals[j])
                        elif val_j != (1 if cl.literals[j] > 0 else -1):
                            return cl
            return None

    def decide(self):
        for v, val in self.assignment.items():
            if val == 0:
                return v
        return None

    def resolve(self, c1_lits, c2_lits, lit):
        s1 = set(c1_lits)
        s2 = set(c2_lits)
        s1.discard(-lit)
        s2.discard(lit)
        return list(s1 | s2)

    def conflict_analysis(self, conflict_clause, level):
        learnt = conflict_clause.literals.copy()
        counter = sum(1 for l in learnt if self.decision_level[abs(l)] == level)
        idx = len(self.stack) - 1
        while counter > 1 and idx >= 0:
            lit, lvl = self.stack[idx]
            var = abs(lit)
            if any(abs(l) == var for l in learnt) and lvl == level:
                ante = self.antecedent[var]
                learnt = self.resolve(learnt, ante.literals, lit)
                counter = sum(1 for l in learnt if self.decision_level[abs(l)] == level)
            idx -= 1
        levels = [self.decision_level[abs(l)] for l in learnt if self.decision_level[abs(l)] < level]
        back_level = max(levels) if levels else 0
        newcl = Clause(learnt, self.use_watched)
        self.clauses.append(newcl)
        if self.use_watched:
            self.watched[newcl.literals[newcl.w1]].append(newcl)
            if newcl.w2 is not None:
                self.watched[newcl.literals[newcl.w2]].append(newcl)
        return newcl, back_level

def cdcl(clauses, num_vars, use_watched=True, conflict_limit=10000):
    formula = CNFFormula(clauses, num_vars, use_watched)
    level = 0
    conflicts = 0

    while True:
        if conflicts > conflict_limit:
            print("Conflict limit exceeded. Aborting.")
            return None, []

        conflict = formula.unit_propagation(level)
        if conflict:
            conflicts += 1
            if level == 0:
                return False, None
            learnt, back = formula.conflict_analysis(conflict, level)
            level = back
            formula.backtrack(back)
            ul = learnt.unit_literal(formula.assignment)
            if ul:
                formula.enqueue(ul, level, learnt)
        else:
            if formula.all_assigned():
                return True, [lit for lit, _ in formula.stack]
            var = formula.decide()
            level += 1
            formula.enqueue(var, level)

def parse_dimacs(path):
    clauses = []
    num_vars = 0
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ('c', '%', '0'):
                continue
            if s.startswith('p cnf'):
                num_vars = int(s.split()[2])
                continue
            lits = list(map(int, s.split()))[:-1]
            clauses.append(lits)
    return clauses, num_vars
