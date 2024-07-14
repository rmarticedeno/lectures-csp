from typing import List
from pydantic_core import from_json
from pydantic import BaseModel, PositiveInt, NonNegativeInt
from parser import RuleParser, NUMBER, PHASE, ROUND, PIPELINE, RESOURCE, GROUP
from ortools.sat.python import cp_model

class JobConfiguration(BaseModel):
    pipeline_count: PositiveInt
    phase_count: PositiveInt
    resource_count: PositiveInt
    round_count: PositiveInt
    group_count: NonNegativeInt
    rule_count: NonNegativeInt
    max_allowed_resource_per_round: NonNegativeInt | None
    rules: str | None
    groups: List[List[PositiveInt]] | None

class JobSolver:
    def __init__(self, configuration: JobConfiguration):
        self.possibilities = configuration.pipeline_count * self.configuration.phase_count * self.configuration.round_count
        self.configuration = configuration
        self.variables = []
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.constrains = RuleParser().parse(configuration.rules) if self.configuration.rule_count else None

    def build(self):
        # add variables
        for i in range(self.configuration.resource_count):
             self.variables = self.model.new_int_var(1, self.possibilities+1, f"{i+1}")
        
        # restrictions

        ## Distinct values per variable
        self.model.add_all_different(self.variables)

        if self.configuration.group_count:
            # apply cummulative restriction for resources on a same schedule
            for group in self.configuration.groups:
                for t in group:
                    group_variables = []
                    for i in range(0, self.configuration.round_count):
                        lower_bound = i * self.configuration.pipeline_count * self.configuration.phase_count + 1
                        upper_bound = i * self.configuration.pipeline_count * self.configuration.phase_count + self.configuration.round_count
                        condition = self.model.NewBoolVar('')
                        group_variables.append(condition)
                        model.add(lower_bound <= self.variables[t-1] <= upper_bound).only_enforce_if(condition)
                    model.add(sum(group_variables) <= self.configuration.max_allowed_resource_per_round)
        
        if self.configuration.rule_count:
            # apply restriction rules

            for restriction in self.constrains:
                targets = []
                rtargets = []
                modificator = 0

                if restriction.lpart.type == RESOURCE:
                    value = restriction.lpart.value
                    targets.append(self.variables[value-1])

                elif restriction.lpart.type == GROUP:
                    value = restriction.lpart.value
                    for v in self.configuration.groups[value-1]:
                        targets.append(self.variables[v-1])

                if restriction.rpart.type == RESOURCE:
                        value = restriction.rpart.value
                        rtargets.append(self.variables[value-1])

                elif restriction.rpart.type == GROUP:
                        value = restriction.rpart.value
                        for v in self.configuration.groups[value-1]:
                            rtargets.append(self.variables[v-1])

                else:
                    value = restriction.rpart.value
                    rtargets.append(value)

                    if restriction.rpart.type == PIPELINE:
                        modificator = self.configuration.pipeline_count

                    elif restriction.rpart.type == ROUND:
                        modificator = self.configuration.pipeline_count

                    elif restriction.rpart.type == PHASE:
                        modificator = self.configuration.phase_count

                if restriction.operator == '=':
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator == rv)
                            else:
                                self.model.add(v == rv)

                elif restriction.operator == '!=':
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator != rv)
                            else:
                                self.model.add(v != rv)

                elif restriction.operator == '>=':
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator >= rv)
                            else:
                                self.model.add(v >= rv)
                
                elif restriction.operator == '<=':
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator <= rv)
                            else:
                                self.model.add(v <= rv)
                
                elif restriction.operator == '<':
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator != rv)
                            else:
                                self.model.add(v != rv)
                
                else:
                    for v in targets:
                        for rv in rtargets:
                            if modificator:
                                self.model.add(v % modificator > rv)
                            else:
                                self.model.add(v > rv)
                




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