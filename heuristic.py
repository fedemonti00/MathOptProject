from instance import Instance
from solver import Solver
import gurobipy as gb


class Heuristic:

    def __init__(self, eta, eta2, threshold):
        self.eta = eta
        self.eta2 = eta2
        self.threshold = threshold
        self.vars_iter_before = []
        instance = Instance()
        self.heuristic_model = Solver(instance) 
        self.last_ref_assigns = {'cat_A' : {},
                                 'cat_A1' : {},
                                 'cat_A2e3' : {}
                                 }

    def create_final_ref_assigns(self):
        for v in self.heuristic_model.model.getVars():
            if v.VarName.startswith("x["):
                i, p = map(int, v.VarName[2:-1].split(','))
                if(i < 15):
                    cat = self.last_ref_assigns.get('cat_A')
                    if str(i) not in list(cat.keys()):
                        cat.update({f'{i}': [p]})
                    else:
                        cat.get(f'{i}').append(p)
                elif(i >= 15 and i < 30):
                    cat = self.last_ref_assigns.get('cat_A1')
                    if str(i) not in list(cat.keys()):
                        cat.update({f'{i}': [p]})
                    else:
                        cat.get(f'{i}').append(p)
                elif(i >= 30 and i < 60):
                    cat = self.last_ref_assigns.get('cat_A2e3')
                    if str(i) not in list(cat.keys()):
                        cat.update({f'{i}': [p]})
                    else:
                        cat.get(f'{i}').append(p)


    def soft_fix_assignments_up(self):
        for name, val in self.vars_iter_before:
            i, p = map(int, name[2:-1].split(','))
            self.heuristic_model.x[i, p].start = 1

    def hard_fix_assignments_up(self):
        for name, val in self.vars_iter_before:
            i, p = map(int, name[2:-1].split(','))
            partita = next((g for g in self.heuristic_model.games + self.heuristic_model.p0 if g[0] == p), None)
            if partita is None:
                continue
            giorno = partita[1]
            if giorno <= self.heuristic_model.t_win:
                self.heuristic_model.x[i, p].lb = 1
                self.heuristic_model.x[i, p].ub = 1
            

    def rolling_horizon(self, i, f, f_prev, refining):
        if i != 0:
            self.heuristic_model.t_win = f_prev
        else:
            self.heuristic_model.t_win = 1
        
        while(True):
            self.heuristic_model.build_model()
            if refining == 0:
                self.soft_fix_assignments_up()
            else:
                self.hard_fix_assignments_up()
            res = self.heuristic_model.solve()
            if res and self.heuristic_model.t_win < f + self.eta:
                self.heuristic_model.t_win += 1
            elif not res:                        
                self.heuristic_model.t_win -= 1
                break
            else:
                break

        while self.heuristic_model.t_win < f + self.eta:
            temp_t_win_container = self.heuristic_model.t_win
            self.heuristic_model.t_win = self.heuristic_model.t_win - self.eta2
            self.heuristic_model.build_model()
            self.hard_fix_assignments_up()
            self.heuristic_model.model.optimize()
            self.vars_iter_before = self.vars_iter_before = [
                                        (v.VarName, v.X)
                                        for v in self.heuristic_model.model.getVars()
                                        if v.VarName.startswith("x[") and v.X > 0.8
                                    ]
            while(True):
                self.heuristic_model.build_model()
                self.hard_fix_assignments_up()
                res = self.heuristic_model.solve()
                if res and self.heuristic_model.t_win < f + self.eta:
                    self.heuristic_model.t_win += 1
                elif not res:                        
                    self.heuristic_model.t_win -= 1
                    break
                else:
                    break

        self.vars_iter_before = [
                                        (v.VarName, v.X)
                                        for v in self.heuristic_model.model.getVars()
                                        if v.VarName.startswith("x[") and v.X > 0.8
                                    ]
        self.create_final_ref_assigns()



    def fix_refine_assignments_up(self, ref_cat_assigns):
        L = set((i, p) for i in ref_cat_assigns.keys() for p in ref_cat_assigns.get(f'{i}'))
        for name, val in self.vars_iter_before:
            i, p = map(int, name[2:-1].split(','))
            if (i, p) not in L:
                self.heuristic_model.x[i, p].ub = 1
                self.heuristic_model.x[i, p].lb = 1
            else:
                self.heuristic_model.x[i, p].start = 0

        self.vars_iter_before = [
                                            (v.VarName, v.X)
                                            for v in self.heuristic_model.model.getVars()
                                            if v.VarName.startswith("x[") and v.X > 0.8
                                        ]


        
    def single_refinement_procedure(self, ref_cat_assigns, i, f, f_prev):
        self.heuristic_model.build_model()
        self.fix_refine_assignments_up(ref_cat_assigns)
        self.rolling_horizon(i, f, f_prev, 1)


    def solve_heuristic(self, i, f, f_prev):

        previousValue = float('inf')
        self.rolling_horizon(i, f, f_prev, 0) 
        incumbentValue = self.heuristic_model.model.ObjVal

        while previousValue - incumbentValue > self.threshold:
            previousValue = incumbentValue
            
            for cat_last_ref_assigns in self.last_ref_assigns.keys():
                self.single_refinement_procedure(self.last_ref_assigns.get(cat_last_ref_assigns),i , f, f_prev)

            incumbentValue = self.heuristic_model.model.ObjVal
    
        return self.heuristic_model.model