import gurobipy as gb

class Solver:

    def __init__(self, instance):
        
        self.teams1 = instance.teams1
        self.teams2 = instance.teams2
        self.games = instance.games
        self.refs = instance.refs
        self.alpha = instance.alpha
        self.beta = instance.beta
        self.third_refs = instance.third_refs
        self.no_home = instance.no_home
        self.no_away = instance.no_away
        self.trips = instance.trips
        self.trips_tilde = instance.trips_tilde
        self.C_E = instance.C_E
        self.C_A = instance.C_A
        self.d = instance.d
        self.r = instance.r
        self.z_A = instance.z_A
        self.z_E = instance.z_E
        self.h = instance.h
        self.t_win = instance.t_win
        self.gamma = instance.gamma
        self.gamma_home = instance.gamma_home
        self.T = instance.T
        self.T_home = instance.T_home
        self.delta = instance.delta
        self.p0 = instance.p0

        self.model = gb.Model("OptimizationModel")

        self.x = None
        self.z = None

    def build_model(self):

        self.x = self.model.addVars([(i, p) for i in range(self.refs) for p in range(self.games)], vtype=gb.GRB.BINARY, name="x")
        self.z = self.model.addVars([(i, v) for i in range(self.refs) for v in range(len(self.trips))], vtype=gb.GRB.BINARY, name="z")

        self.model.setObjective(
            gb.quicksum(self.d[v.k, v.m] * self.z[i, v.id] for i in range(self.refs) for v in self.trips_tilde if v.k > 0 and v.m > 0) +
            gb.quicksum(self.r[i, v.k] * self.z[i, v.id] for i in range(self.refs) for v in self.trips_tilde if v.k > 0 and v.m == 0) +
            gb.quicksum(self.r[i, v.m] * self.z[i, v.id] for i in range(self.refs) for v in self.trips_tilde if v.k == 0 and v.m > 0) +
            gb.quicksum(self.h * v.s * self.z[i, v.id] for i in range(self.refs) for v in self.trips_tilde if v.k > 0 and v.m > 0 and self.z_A[i] != self.z_E[v.k]),
            gb.GRB.MINIMIZE
        )

        for i in range(self.refs):
            self.model.addRange(
                gb.quicksum(self.x[i, p.id] for p in self.games if p.k > 0 and p.t <= self.t_win),
                self.alpha[i], self.beta[i],
                name="2) Constraint on the number of referee's games"
            )

        for i in range(self.refs):
            for k in range(1, self.teams):
                for q in range(1, self.T[k] - self.gamma):
                    self.model.addConstr(
                        gb.quicksum(self.x[i, p] for p in self.games_for_team_in_range(k, q, self.gamma)) <= 1,
                        name="3) Constraint to avoid consecutive team's games with the same ref"
                    )
        
        for i in range(self.refs):
            for k in range(1, self.teams):
                for q in range(1, self.T_home[k] - self.gamma_home):
                    self.model.addConstr(
                        gb.quicksum(self.x[i, p] for p in self.home_games_for_team_in_range(k, q, self.gamma_home)) <= 1,
                        name="4) Constraint to avoid consecutive home team's games with the same ref"
                    )

        for i in range(self.refs):
            for q in range(1, self.t_win - self.delta[i] + 1):
                self.model.addConstr(
                    gb.quicksum(self.x[i, self.p0[t]] for t in range(q, q + self.delta[i])) >= 1,
                    name="5) Constraint to avoid that a ref to stay too much time away from home"
                )

        for i in range(self.refs):
            for q in range(1, self.t_win - 4):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p.id] for p in self.games
                                if p.t in range(q, q + 5) and p.k > 0) <= 3,
                    name="6) Constraint to avoid that a ref officiate more than three games in a win of 5 days"
                )

        for (i, k) in self.no_home:
            for p in range(self.games):
                if p.k == k:
                    self.model.addConstr(self.x[i, p.id] == 0, name="7) Constraint to Constraint to prohibit a referee from officiating specific home teams")

        for (i, l) in self.no_away:
            for p in range(self.games):
                if p.l == l:
                    self.model.addConstr(self.x[i, p.id] == 0, name="8) Constraint to prohibit a referee from officiating specific away teams")

        for p in range(self.games):
            if p.k in self.teams1 and p.t <= self.t_win:
                self.model.addConstr(gb.quicksum(self.x[i, p.id] for i in self.refs.cat_A) == 1, name="9) Ref from cat A")
                self.model.addConstr(gb.quicksum(self.x[i, p.id] for i in self.refs.cat_A1) == 1, name="9) Ref from cat A1")
                self.model.addConstr(gb.quicksum(self.x[i, p.id] for i in self.refs.cat_A2 + self.refs.cat_A3) == 1, name="9) Ref from cat A2 or cat A3")
            elif p.k in self.teams2 and p.t <= self.t_win:
                self.model.addConstr(gb.quicksum(self.x[i, p.id] for i in self.refs.cat_A + self.refs.cat_A1 + self.refs.cat_A2) == 1, name="10) Ref from cat A or cat A1 or cat A2")
                self.model.addConstr(gb.quicksum(self.x[i, p.id] for i in self.refs.cat_A2 + self.refs.cat_A3) == 1, name="10) Ref from cat A2 or cat A3")
        
        for i in range(self.refs):
            for q in range(1, self.t_win + 1):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p.id] for p in range(self.games) if p.t == q) <= 1,
                    name="11) Constraint to avoid that a ref officiating two game in a single day"
                )

        for i in range(self.refs):
            for q in range(1, self.t_win + 1):
                self.model.addConstr(
                    gb.quicksum(self.z[i, v.id] for v in self.trips_tilde if v.t == q) <= 1,
                    name="12) Constraint to avoid that a ref initiate more than a trip in a single day"
                )

        for i in range(self.refs):
            for q in range(1, self.t_window + 1):
                self.model.addConstr(
                    gb.quicksum(self.z[i, v.id] for v in self.trips_tilde if v.t == q and v.s == 2) +
                    gb.quicksum(self.z[i, v.id] for v in self.trips_tilde if v.t == q + 1) <= 1,
                    name="13) Constraint to avoid that a ref initiate trip if he/she has just finished a two day trip"
                )

        for i in range(self.refs):
            for q in range(1, self.t_win):
                for v in self.trips:
                    if v.t < q and v.s == 1:
                        p1 = self.get_game(t=v.t, k=v.k)
                        p2 = self.get_game(t=v.t + 1, k=v.m)
                        if p1 is not None and p2 is not None:
                            self.model.addConstr(self.x[i, p1.id] + self.x[i, p2.id] <= 1 + self.z[i, v.id], name="14) Constraint to force connected z and x to be 1")
                            self.model.addConstr(2 * self.z[i, v.id] <= self.x[i, p1.id] + self.x[i, p2.id], name="14) Constraint to force connected z and x to be 1")

        for i in range(self.refs):
            for q in range(1, self.t_window - 1):
                for v_cap in self.trips:
                    if v_cap.t < q and v_cap.s == 2:
                        p1 = self.get_game(t=v_cap.t, home=v_cap.k)
                        p2 = self.get_game(t=v_cap.t + 2, home=v_cap.m)
                        if p1 is not None and p2 is not None:
                            # Somma dei viaggi da t=q con durata 1
                            z_sum = gb.quicksum(
                                self.z[i, v_tilde.id]
                                for v_tilde in self.trips
                                if v_tilde.t == q and v_tilde.s == 1
                            )
                            self.model.addConstr(
                                self.x[i, p1.id] + self.x[i, p2.id] <= 1 + self.z[i, v_cap.id] + z_sum,
                                name="15) Constraint to force connected z and x to be 1"
                            )
                            self.model.addConstr(
                                2 * self.z[i, v_cap.id] <= self.x[i, p1.id] + self.x[i, p2.id],
                                name="15) Constraint to force connected z and x to be 1"
                            )

        for i in range(self.refs):
            for q in range(1, self.t_win):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p.id] for p in range(self.games) if p.t == q) + 
                    gb.quicksum(self.x[i, p.id] for p in range(self.games) if p.t == q + 1) >= 1,
                    name="16) Constraint to assign a ref at least one game (real or fictious) every two days"
        )

        for i in range(self.refs):
            for v in self.trips_tilde:
                if v.s == 1:
                    if (v.k, v.m) in self.CE:
                        self.model.addConstr(self.z[i, v.id] == 0, name="17) Constraint to avoid unfeasible trip")
                    if v.k == 0 and (i, v.m) in self.CA:
                        self.model.addConstr(self.z[i, v.id] == 0, name="17) Constraint to avoid unfeasible trip")
                    if v.m == 0 and (i, v.k) in self.CA:
                        self.model.addConstr(self.z[i, v.id] == 0, name="17) Constraint to avoid unfeasible trip")
