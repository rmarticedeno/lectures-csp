from src import JobConfiguration, JobSolver

t = JobConfiguration

t.pipeline_count = 4
t.phase_count = 4
t.resource_count = 40
t.round_count = 4
t.group_count = 0
t.rule_count = 0
# t.max_allowed_resource_per_round: NonNegativeInt | None
# t.rules: str | None
# t.groups: List[List[PositiveInt]] | None

s = JobSolver(configuration=t)
s.build()
s.solve()