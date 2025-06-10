from instance import Instance
from solver import Solver
from heuristic import Heuristic


for i in range(1,67):
    instance = Instance()
    instance.t_win = i
    solver = Solver(instance)
    solver.build_model()
    res = solver.solve()
    
    if res:
        with open(f"solution/model/soluzione_{i}.txt", "w") as f:
            f.write(f"Time to resolve: {round(solver.model.Runtime)}\n\n")
            
            f.write(f"Obj: {solver.model.ObjVal}\n\n")

            f.write("Variabili x con valore 1:\n")
            for v in solver.model.getVars():
                if v.VarName.startswith("x[") and v.X > 0.5:
                    f.write(f"{v.VarName}: {v.X}\n")

            f.write("\nVariabili z con valore 1:\n")
            for v in solver.model.getVars():
                if v.VarName.startswith("z[") and v.X > 0.5:
                    f.write(f"{v.VarName}: {v.X}\n")
    else:
        break

heuristic = Heuristic(5, 3, 100)
last_day = instance.games[len(instance.games) - 1][1]
f_i = [i*14 for i in range(1,last_day + 1) if i*14 < last_day]
f_i.append(last_day - 5)
for i, f in enumerate(f_i):
    days = f + 5
    with open("wat.txt", "a") as f_out:
        f_out.write(f'Sono al giro f = {f}')
    res_model = None
    if i != 0:
        res_model = heuristic.solve_heuristic(i, f, f_i[i - 1])
    else:
        res_model = heuristic.solve_heuristic(i, f, 1)
    with open(f"solution/heuristic/soluzione_heuristic_new.txt", "a") as f_out:
        f_out.write(f"Game until: {days}\n\n")

        f_out.write(f"Obj: {res_model.ObjVal}\n\n")

        f_out.write("Variabili x con valore 1:\n")
        for v in res_model.getVars():
            if v.VarName.startswith("x[") and v.X > 0.5:
                f_out.write(f"{v.VarName}: {v.X}\n")

        f_out.write("\nVariabili z con valore 1:\n")
        for v in res_model.getVars():
            if v.VarName.startswith("z[") and v.X > 0.5:
                f_out.write(f"{v.VarName}: {v.X}\n")