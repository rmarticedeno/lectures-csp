from typing import List
from pydantic_core import from_json
from pydantic import BaseModel, PositiveInt, NonNegativeInt
from .parser import RuleParser, NUMBER, PHASE, ROUND, PIPELINE, RESOURCE, GROUP
from ortools.sat.python import cp_model
from operator import gt, lt, ge, le, eq, ne

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
        self.possibilities = configuration.pipeline_count * configuration.phase_count * configuration.round_count
        self.configuration = configuration
        self.variables = []
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.constrains = RuleParser().parse(configuration.rules) if self.configuration.rule_count else None

    def build(self):
        # add variables
        for i in range(self.configuration.resource_count):
             self.variables.append(self.model.new_int_var(1, self.possibilities+1, f"{i+1}"))
        
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
                        self.model.add(self.variables[t-1] >= lower_bound).only_enforce_if(condition)
                        self.model.add(self.variables[t-1] <= upper_bound).only_enforce_if(condition)
                    self.model.add(sum(group_variables) <= self.configuration.max_allowed_resource_per_round)
        
        if self.configuration.rule_count:
            # apply restriction rules

            for restriction in self.constrains:
                targets = []
                rtargets = []
                modificator = lambda x : x
                
                op_dict = {
                    '=': eq,
                    '!=': ne,
                    '>=': ge,
                    '<=': le,
                    '<': lt,
                    '>': gt,  
                }

                # Left side of the comparison
                if restriction.lpart.type == RESOURCE:
                    value = restriction.lpart.value
                    targets.append(self.variables[value-1])

                elif restriction.lpart.type == GROUP:
                    value = restriction.lpart.value
                    for v in self.configuration.groups[value-1]:
                        targets.append(self.variables[v-1])

                # right side of the comparison
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

                for v in targets:
                    for rv in rtargets:
                        lpart = v
                        rpart = rv
                        oper = op_dict[restriction.operator]

                        if restriction.rpart.type == PHASE:
                            ## lambda x : (x - 1) % self.configuration.phase_count + 1
                            mod = self.model.NewIntVar(0, self.configuration.phase_count, '')
                            self.model.add_modulo_equality(mod, v - 1, self.configuration.phase_count)
                            lpart = mod
                            rpart = rv - 1

                        elif restriction.rpart.type == PIPELINE:
                            ## lambda x : (x - 1) // self.configuration.pipeline_count + 1
                            div = self.model.NewIntVar(0, self.configuration.pipeline_count, '')
                            self.model.add_division_equality(div, v - 1, self.configuration.pipeline_count)
                            lpart = div
                            rpart = rv - 1

                        elif restriction.rpart.type == ROUND:
                            ## lambda x : ((x - 1 - (x - 1) % self.configuration.phase_count) / self.configuration.phase_count ) % self.configuration.pipeline_count + 1
                            mod1 =self. model.NewIntVar(0, self.configuration.phase_count, '')
                            self.model.add_modulo_equality(mod1, v - 1, self.configuration.phase_count)
                            div = self.model.NewIntVar(0, self.possibilities +1 , '')
                            self.model.add_division_equality(div, v - 1 - mod1, self.configuration.phase_count)
                            mod2 = self.model.NewIntVar(0, self.configuration.pipeline_count, '')
                            self.model.add_modulo_equality(mod2, div, self.configuration.pipeline_count)
                            lpart = mod2
                            rpart = rv - 1

                        self.model.add(oper(lpart, rpart))
                
    def solve(self):
        status = self.solver.solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Solution:")

            print(f"Optimal Schedule Length: {self.solver.objective_value}")
            for x in self.variables:
                print(x, self.solver.value(x))

        # Statistics.
        print("\nStatistics")
        print(f"  - conflicts: {self.solver.num_conflicts}")
        print(f"  - branches : {self.solver.num_branches}")
        print(f"  - wall time: {self.solver.wall_time}s")