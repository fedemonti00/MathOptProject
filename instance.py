import re
import random

class Instance:

    def __init__(self):
        games_info = self.open_games()
        zone_info = self.open_zone_info()
        unfeasible_trips = self.unfeasible_trips()


        self.teams1 = [team_id for team_id in range(0,21)]
        self.teams2 = []
        self.games = games_info[0]
        self.games_teams = games_info[1]
        self.home_games_teams = games_info[2]
        trips_info = self.open_trips()
        self.refs = [[ref_id for ref_id in range(i*15, (i+1)*15)] for i in range(4)]
        self.alpha = []
        self.beta = []
        for i in range(60):
                self.alpha.append(0)
                self.beta.append(5)
        self.no_home = zone_info[0]
        self.no_away = zone_info[1]
        self.trips = trips_info[0]
        self.trips_tilde = trips_info[1]
        self.C_E = unfeasible_trips[0]
        self.C_A = unfeasible_trips[1]
        self.d = self.open_team_cost()
        self.r = self.open_ref_cost()
        self.Z_A = zone_info[2]
        self.Z_E = zone_info[3]
        self.h = 10
        self.t_win = 67
        self.gamma = 3
        self.gamma_home = 1
        self.T = games_info[3]
        self.T_home = games_info[4]
        self.delta = [14 for i in range(60)]
        self.p0 = [(len(self.games) - 1 + t, t, 0 , 0) for t in range(67)]
        self.n_refs = 60


    def open_team_cost(self):
        d = [[]]


        for team in range(1,21):
            input_distances = f"data/cost/teams/{team}.txt"
            d_team = [float(0.0)]

            with open(input_distances, "r", encoding="utf-8") as fin:       
                lines = fin.readlines()[1:]
                for line in lines:
                    cost = re.split(r"\s{2,}", line.strip())[3]
                    d_team.append(float(cost.replace("$", "").replace(",", "")))

                d.append(d_team)

        return d
    
    def open_games(self):
        input = f"data/games_id.txt"
        games = []

        with open(input, "r", encoding="utf-8") as fin:       
            lines = fin.readlines()[1:]
            for i, line in enumerate(lines):
                parsed_line = re.split(r"\s{1,}", line.strip())
                game = parsed_line[1].split("-")
                games.append((i, int(parsed_line[0]), int(game[0]), int(game[1])))

        games_team = [[] for i in range(0,21)]
        home_games_team = [[] for i in range(0,21)]
        for tuple in games:
                games_team[tuple[2]].append(tuple)
                games_team[tuple[3]].append(tuple)
                home_games_team[tuple[2]].append(tuple)

        games_team[0] = [(179 + t, t, 0 , 0) for t in range(67)]
        home_games_team[0] = [(179 + t, t, 0 , 0) for t in range(67)]

        T = [len(team) for team in games_team]
        T_home = [len(team) for team in home_games_team]

        return [games, games_team, home_games_team, T, T_home]

    def open_trips(self):
        trips = []
        trips_tilde = []

        games_all = self.games + [(len(self.games) + t, t, 0 , 0) for t in range(68)] 

        from collections import defaultdict
        games_by_day = defaultdict(list)
        for g in games_all:
            game_id, day, home, away = g
            games_by_day[day].append((game_id, home, away))

        for t in range(max(giorno for _, giorno, _, _ in games_all) + 1):
            for tipo in [1, 2]:
                t2 = t + tipo
                if t2 not in games_by_day:
                    continue
                for g1 in games_by_day[t]:
                    id1, h1, a1 = g1
                    for g2 in games_by_day[t2]:
                        id2, h2, a2 = g2
                        trips.append((tipo, t, h1, h2, a2))
                        trips_tilde.append((tipo, t, h1, h2))

        return [trips, trips_tilde]
    
    def open_zone_info(self):
        input = f"data/teams.txt"
        Z_E = []

        with open(input, "r", encoding="utf-8") as fin:       
            lines = fin.readlines()[1:]
            for line in lines:
                parsed_line = re.split(r"\\", line.strip())
                Z_E.append(parsed_line[2])


        input = f"data/referee.txt"
        Z_A = []

        with open(input, "r", encoding="utf-8") as fin:       
            lines = fin.readlines()
            for i, line in enumerate(lines):
                parsed_line = re.split(r"\\", line.strip())
                Z_A.append(parsed_line[2])


        no_home = []
        no_away = []

        for ref_id, ref_zone in enumerate(Z_A):
            for team_id, team_zone in enumerate(Z_E):
                if ref_zone == team_zone:
                    no_home.append((ref_id, team_id))
                    no_away.append((ref_id, team_id))

        return [no_home, no_away, Z_A, Z_E]
    
    def unfeasible_trips(self):
        C_E = []
        C_A = []

        for team in range(1,21):
            input_distances = f"data/cost/teams/{team}.txt"

            with open(input_distances, "r", encoding="utf-8") as fin:
                lines = fin.readlines()[1:]
                for line, i in zip(lines, range(1, 21)):
                    if team != i:
                        distance = int(line.split("  ")[2])
                        if distance > 1500:
                            C_E.append((team, i))

        for ref in range(0,60):
            input_distances = f"data/cost/ref/{ref}.txt"

            with open(input_distances, "r", encoding="utf-8") as fin:
                lines = fin.readlines()[1:]
                for line, team in zip(lines, range(1, 21)):
                        distance = int(line.split("  ")[2])
                        if distance > 1500:
                            C_A.append((ref, team))


        return [C_E, C_A]
    
    def open_ref_cost(self):
        r = []


        for ref in range(0,60):
            input_distances = f"data/cost/ref/{ref}.txt"
            r_ref = [float(0.0)]

            with open(input_distances, "r", encoding="utf-8") as fin:       
                lines = fin.readlines()[1:]
                for line in lines:
                    cost = re.split(r"\s{2,}", line.strip())[3]
                    r_ref.append(float(cost.replace("$", "").replace(",", "")))

                r.append(r_ref)

        
        return r
