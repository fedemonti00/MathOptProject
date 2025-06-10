import gurobipy as gb

class Solver:

    def __init__(self, instance):
        
        self.teams1 = instance.teams1
        self.teams2 = instance.teams2
        self.games = instance.games
        self.games_teams = instance.games_teams
        self.home_games_teams = instance.home_games_teams
        self.refs = instance.refs
        self.alpha = instance.alpha
        self.beta = instance.beta
        self.no_home = instance.no_home
        self.no_away = instance.no_away
        self.trips = instance.trips
        self.trips_tilde = instance.trips_tilde
        self.C_E = instance.C_E
        self.C_A = instance.C_A
        self.d = instance.d
        self.r = instance.r
        self.Z_A = instance.Z_A
        self.Z_E = instance.Z_E
        self.h = instance.h
        self.t_win = instance.t_win
        self.gamma = instance.gamma
        self.gamma_home = instance.gamma_home
        self.T = instance.T
        self.T_home = instance.T_home
        self.delta = instance.delta
        self.p0 = instance.p0
        self.n_refs = instance.n_refs

        self.model = None

    def games_for_team_in_range(self, k, home):
        games_in_range = []
        if(not home):
            for q in range(1, self.T[k] - self.gamma + 1):
                games_in_range.append(self.games_teams[k][q])
        else:
            for q in range(1, self.T_home[k] - self.gamma_home + 1):
                games_in_range.append(self.home_games_teams[k][q])
        
        return games_in_range
    
    def get_game(self, t, k):
        return self.games_teams[k][t]


    def build_model(self):
        self.model = gb.Model("OptimizationModel")
<<<<<<< HEAD
        self.model.setParam("TimeLimit", 1800)
=======
        self.model.setParam("TimeLimit", 3600)
>>>>>>> 559fa09e3d935fd2f0c0c2b5b0d71019d882c384
        self.x = self.model.addVars([(i, p) for i in range(self.n_refs) for p in range(len(self.games) + len(self.p0))], vtype=gb.GRB.BINARY, name="x")
        self.z = self.model.addVars([(i, v) for i in range(self.n_refs) for v in range(len(self.trips))], vtype=gb.GRB.BINARY, name="z")

        self.model.setObjective(
            gb.quicksum(self.d[k][m] * self.z[i, id] for i in range(self.n_refs) for id, (s, t, k, m) in enumerate(self.trips_tilde) if k > 0 and m > 0) +
            gb.quicksum(self.r[i][k] * self.z[i, id] for i in range(self.n_refs) for id, (s, t, k, m) in enumerate(self.trips_tilde) if k > 0 and m == 0) +
            gb.quicksum(self.r[i][m] * self.z[i, id] for i in range(self.n_refs) for id, (s, t, k, m) in enumerate(self.trips_tilde) if k == 0 and m > 0) +
            gb.quicksum(self.h * s * self.z[i, id] for i in range(self.n_refs) for id, (s, t, k, m) in enumerate(self.trips_tilde) if k > 0 and m > 0 and self.Z_A[i] != self.Z_E[k]),
            gb.GRB.MINIMIZE
        )

        for i in range(self.n_refs):
            self.model.addRange(
                gb.quicksum(self.x[i, p[0]] for p in self.games if p[2] > 0 and p[1] <= self.t_win),
                float(self.alpha[i]), float(self.beta[i]),
                name="2)_Constraint_on_the_number_of_referee's_games"
            )

        for i in range(self.n_refs):
            for k in range(1, 21):
                games_k = sorted(self.games_teams[k], key=lambda x: x[1])
                for t in range(len(games_k) - self.gamma + 1):
                    window = games_k[t:t + self.gamma]
                    self.model.addConstr(
                        gb.quicksum(self.x[i, p[0]] for p in window) <= 1,
                        name=f"3)_No_consec_games_team_{k}_ref_{i}_start_{window[0][1]}"
                    )


        for i in range(self.n_refs):
            for k in range(1, 21):
                games_k = sorted(self.home_games_teams[k], key=lambda x: x[1]) 
                for t in range(len(games_k) - self.gamma_home + 1):
                    window = games_k[t:t + self.gamma_home]
                    self.model.addConstr(
                        gb.quicksum(self.x[i, p[0]] for p in window) <= 1,
                        name=f"4)_No_consec_games_team_{k}_ref_{i}_start_{window[0][1]}"
                    )

        for i in range(self.n_refs):
            for q in range(1, self.t_win - self.delta[i] + 1):
                self.model.addConstr(
                    gb.quicksum(self.x[i, self.p0[t][0]] for t in range(q, q + self.delta[i])) >= 1,
                    name="5)_Constraint_to_avoid_that_a_ref_to_stay_too_much_time_away_from_home"
                )

        for i in range(self.n_refs):
            for q in range(1, self.t_win - 4):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p[0]] for p in self.games
                                if p[1] in range(q, q + 5) and p[2] > 0) <= 3,
                    name="6)_Constraint_to_avoid_that_a_ref_officiate_more_than_three_games_in_a_win_of_5_days"
                )

        for (i, k) in self.no_home:
            self.model.addConstr(
                gb.quicksum(self.x[i, p[0]] for p in self.games if p[2] == k)  == 0, 
                name="7)_Constraint_to_Constraint_to_prohibit_a_referee_from_officiating_specific_home_teams")

        for (i, l) in self.no_away:            
            self.model.addConstr(
                    gb.quicksum(self.x[i, p[0]] for p in self.games if p[3] == l)  == 0, 
                            name="8)_Constraint_to_prohibit_a_referee_from_officiating_specific_away_teams")

        for p in self.games:
            if p[2] in self.teams1 and p[1] <= self.t_win:
                self.model.addConstr(gb.quicksum(self.x[i, p[0]] for i in self.refs[0]) == 1, name="9)_Ref_from_cat_A")
                self.model.addConstr(gb.quicksum(self.x[i, p[0]] for i in self.refs[1]) == 1, name="9)_Ref_from_cat_A1")
                self.model.addConstr(gb.quicksum(self.x[i, p[0]] for i in self.refs[2] + self.refs[3]) == 1, name="9)_Ref_from_cat_A2_or_cat_A3")
            elif p[2] in self.teams2 and p[1] <= self.t_win:
                self.model.addConstr(gb.quicksum(self.x[i, p[0]] for i in self.refs[0] + self.refs[1] + self.refs[2]) == 1, name="10)_Ref_from_cat_A_or_cat_A1_or_cat_A2")
                self.model.addConstr(gb.quicksum(self.x[i, p[0]] for i in self.refs[2] + self.refs[3]) == 1, name="10)_Ref_from_cat_A2_or_cat_A3")
        
        for i in range(self.n_refs):
            for q in range(1, self.t_win + 1):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p[0]] for p in self.games + self.p0 if p[1] == q) <= 1,
                    name="11)_Constraint_to_avoid_that_a_ref_officiating_two_game_in_a_single_day"
                )

        for i in range(self.n_refs):
            for q in range(1, self.t_win + 1):
                self.model.addConstr(
                    gb.quicksum(self.z[i, id] for id, v in enumerate(self.trips_tilde) if v[1] == q) <= 1,
                    name="12)_Constraint_to_avoid_that_a_ref_initiate_more_than_a_trip_in_a_single_day"
                )

        for i in range(self.n_refs):
            for q in range(1, self.t_win + 1):
                self.model.addConstr(
                    gb.quicksum(self.z[i, id] for id, v in enumerate(self.trips_tilde) if v[1] == q and v[0] == 2) +
                    gb.quicksum(self.z[i, id] for id, v in enumerate(self.trips_tilde) if v[1] == q + 1) <= 1,
                    name="13)_Constraint_to_avoid_that_a_ref_initiate_trip_if_he/she_has_just_finished_a_two_day_trip"
                )

        for i in range(self.n_refs):
            for q in range(self.t_win):
                for p1 in self.games + self.p0:
                    if p1[1] == q:
                        for id, (s,t,k,m,n) in enumerate(self.trips):
                            if s == 1 and t == q and k == p1[2]:
                                p2 = next((g for g in self.games_teams[m] if g[1] == q + 1), None)
                                if p2 is not None:
                                    self.model.addConstr(self.x[i, p1[0]] + self.x[i, p2[0]] <= 1 + self.z[i, id], name="14)_Constraint_to_force_connected_z_and_x_to_be_1")
                                    self.model.addConstr(2 * self.z[i, id] <= self.x[i, p1[0]] + self.x[i, p2[0]], name="14)_Constraint_to_force_connected_z_and_x_to_be_1")

        for i in range(self.n_refs):
            for q in range(self.t_win - 1):
                for p1 in self.games + self.p0:
                    if p1[1] == q:
                        for id, (s,t,k,m,n) in enumerate(self.trips):
                            if s == 2 and t == q and k == p1[2]:
                                p2 = next((g for g in self.games_teams[m] if g[1] == q + 2), None)
                                if p2 is not None:
                                    z_sum = gb.quicksum(
                                        self.z[i, id_tilde]
                                        for id_tilde, v_tilde in enumerate(self.trips_tilde)
                                        if v_tilde[1] == q and v_tilde[0] == 1
                                    )
                                    self.model.addConstr(
                                        self.x[i, p1[0]] + self.x[i, p2[0]] <= 1 + self.z[i, id] + z_sum,
                                        name="15)_Constraint_to_force_connected_z_and_x_to_be_1"
                                    )
                                    self.model.addConstr(
                                        2 * self.z[i, id] <= self.x[i, p1[0]] + self.x[i, p2[0]],
                                        name="15)_Constraint_to_force_connected_z_and_x_to_be_1"
                                    )


        for i in range(self.n_refs):
            for q in range(1, self.t_win):
                self.model.addConstr(
                    gb.quicksum(self.x[i, p[0]] for p in self.games + self.p0 if p[1] == q) + 
                    gb.quicksum(self.x[i, p[0]] for p in self.games + self.p0 if p[1] == q + 1) >= 1,
                    name="16)_Constraint_to_assign_a_ref_at_least_one_game_(real_or_fictious)_every_two_days"
        )

        for i in range(self.n_refs):
            for id, v in enumerate(self.trips_tilde):
                if v[0] == 1:
                    if (v[2], v[3]) in self.C_E:
                        self.model.addConstr(self.z[i, id] == 0, name="17)_Constraint_to_avoid_unfeasible_trip")
                    if v[2] == 0 and (i, v[3]) in self.C_A:
                        self.model.addConstr(self.z[i, id] == 0, name="17)_Constraint_to_avoid_unfeasible_trip")
                    if v[3] == 0 and (i, v[2]) in self.C_A:
                        self.model.addConstr(self.z[i, id] == 0, name="17)_Constraint_to_avoid_unfeasible_trip")


    def solve(self):
        self.model.optimize()
        
        if self.model.status == gb.GRB.INFEASIBLE:
            print("⚠️ Model infeasible. Computing IIS...")
            self.model.computeIIS()
            self.model.write("infeasible.ilp")     
            self.model.write("infeasible.lp")   
            print("✅ IIS written to 'infeasible.ilp' and 'infeasible.lp'")

        if self.model.status == gb.GRB.OPTIMAL:
            return True
        
        if self.model.status == gb.GRB.TIME_LIMIT:
            return False



    def debug(self):
        self.model.computeIIS()
        self.model.write("model.ilp")
        self.model.write("infeasible.ilp")
