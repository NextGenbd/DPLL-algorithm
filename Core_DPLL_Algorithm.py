import sys

from collections import deque

class Clause:
    def __init__(self, literals, use_watched):
        self.literals = literals  # list of ints ending without 0
        self.size = len(literals)
        self.use_watched = use_watched
        # watched indices
        if use_watched:
            if self.size >= 2:
                self.w1, self.w2 = 0, 1
            elif self.size == 1:
                self.w1 = self.w2 = 0
        else:
            self.w1 = self.w2 = None

    def is_satisfied(self, assignment):
        return any((assignment[abs(l)] == (1 if l>0 else -1)) for l in self.literals)

    def is_conflict(self, assignment):
        # all literals assigned false
        for l in self.literals:
            val = assignment[abs(l)]
            if val == 0 or val == (1 if l>0 else -1):
                return False
        return True

    def unit_literal(self, assignment):
        # returns literal if clause is unit; else None
        unassigned = []
        for l in self.literals:
            val = assignment[abs(l)]
            if val == 0:
                unassigned.append(l)
            elif val == (1 if l>0 else -1):
                return None
        if len(unassigned) == 1:
            return unassigned[0]
        return None

class CNFFormula:
    def __init__(self, clauses, num_vars, use_watched=True):
        self.num_vars = num_vars
        self.assignment = [0] * (num_vars + 1)  # 0=unassigned, 1=true, -1=false
        self.decision_level = [0] * (num_vars + 1)
        self.antecedent = [None] * (num_vars + 1)
        self.stack = []  # (lit, level)
        self.clauses = [Clause(c, use_watched) for c in clauses]
        self.use_watched = use_watched
        # watched lists: literal->list of clauses
        if use_watched:
            self.watched = {i: [] for i in range(-num_vars, num_vars+1) if i!=0}
            for cl in self.clauses:
                self.watched[cl.literals[cl.w1]].append(cl)
                if cl.w2 is not None:
                    self.watched[cl.literals[cl.w2]].append(cl)

    def all_assigned(self):
        return all(v != 0 for v in self.assignment[1:])

    def enqueue(self, lit, level, ante=None):
        var = abs(lit)
        self.assignment[var] = 1 if lit>0 else -1
        self.decision_level[var] = level
        self.antecedent[var] = ante
        self.stack.append((lit, level))

    def backtrack(self, level):
        while self.stack and self.stack[-1][1] > level:
            lit, lvl = self.stack.pop()
            var = abs(lit)
            self.assignment[var] = 0
            self.antecedent[var] = None
            self.decision_level[var] = 0

    def unit_propagation(self, level):
        queue = deque()
        # initial unit clauses
        for cl in self.clauses:
            ul = cl.unit_literal(self.assignment)
            if ul is not None:
                queue.append((cl, ul))
        while queue:
            cl, lit = queue.popleft()
            var = abs(lit)
            val = self.assignment[var]
            if val != 0 and val != (1 if lit>0 else -1):
                return cl  # conflict
            if val == 0:
                self.enqueue(lit, level, cl)
                # after assign, check for new unit or conflict
                for c in self.clauses:
                    if c.is_satisfied(self.assignment): continue
                    ul2 = c.unit_literal(self.assignment)
                    if ul2 is not None:
                        queue.append((c, ul2))
                    elif c.is_conflict(self.assignment):
                        return c
        return None

    def decide(self):
        # simple heuristic: select the first unassigned var everytime.
        for v in range(1, self.num_vars+1):
            if self.assignment[v] == 0:
                return v
        return None

    def resolve(self, c1_lits, c2_lits, lit):
        # c1_lits and c2_lits are lists of literals
        s1 = set(c1_lits)
        s2 = set(c2_lits)
        s1.discard(-lit)
        s2.discard(lit)
        return list(s1.union(s2))

    def conflict_analysis(self, conflict_clause, level):
        # First UIP learning
        learnt = list(conflict_clause.literals)
        counter = sum(1 for l in learnt if self.decision_level[abs(l)] == level)
        idx = len(self.stack)-1
        while counter > 1 and idx >= 0:
            lit, lvl = self.stack[idx]
            var = abs(lit)
            if any(abs(l) == var for l in learnt) and lvl == level:
                ante = self.antecedent[var]
                learnt = self.resolve(learnt, ante.literals, lit)
                counter = sum(1 for l in learnt if self.decision_level[abs(l)] == level)
            idx -= 1
        # find backtrack level
        levels = [self.decision_level[abs(l)] for l in learnt if self.decision_level[abs(l)] < level]
        back_level = max(levels) if levels else 0
        # add learnt clause
        newcl = Clause(learnt, self.use_watched)
        self.clauses.append(newcl)
        return newcl, back_level


def cdcl(clauses, num_vars, use_watched=True, conflict_limit=1000):
    formula = CNFFormula(clauses, num_vars, use_watched)
    level = 0
    decisions = 0
    while True:
        conflict = formula.unit_propagation(level)
        if conflict:
            if level == 0:
                return False, None
            learnt, back = formula.conflict_analysis(conflict, level)
            level = back
            formula.backtrack(back)
            # enqueue unit the learnt clause's unit literal
            ul = learnt.unit_literal(formula.assignment)
            if ul is not None:
                formula.enqueue(ul, level, learnt)
        else:
            if formula.all_assigned():
                return True, [l for l,_ in formula.stack]
            # decide next literal
            var = formula.decide()
            level += 1
            decisions += 1
            formula.enqueue(var, level)

def parse_dimacs(path):
    clauses = []
    num_vars = 0
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped[0] in ('c','%','0'):
                continue
            if stripped.startswith('p cnf'):
                parts=stripped.split()
                num_vars=int(parts[2])
                continue
            lits=list(map(int,stripped.split()))[:-1]
            clauses.append(lits)
    return clauses, num_vars

# Contains Clause, CNFFormula, cdcl, parse_dimacs functions
