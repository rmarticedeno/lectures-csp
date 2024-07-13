import collections
from ortools.sat.python import cp_model

classrooms = 11
lectures_per_day = 6
days = 7
courses = 10
lessons = 144

all_classrooms = classrooms * lectures_per_day * days


model = cp_model.CpModel()

distribution = []

for i in range(lessons):
    distribution.append(model.new_int_var(1, lessons+1, f"Lesson_{i+1}"))

model.add_all_different(distribution)

model.add(distribution[0] == 120)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution:")

        print(f"Optimal Schedule Length: {solver.objective_value}")
        for x in distribution:
            print(x, solver.value(x))
else:
    print("No solution found.")

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts: {solver.num_conflicts}")
    print(f"  - branches : {solver.num_branches}")
    print(f"  - wall time: {solver.wall_time}s")