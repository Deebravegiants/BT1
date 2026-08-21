# Q3648: Guard evaluated once but relied on continuously in run (plans/idle.rs)

## Question
Can an unprivileged attacker satisfy a condition once at the entry of `run` in [src/plans/idle.rs](src/plans/idle.rs) (presence, distance, verdict) and then violate it for the remainder of the stage, since the guard is not re-evaluated?

## Target
- File/function: [src/plans/idle.rs](src/plans/idle.rs) -> `run` (function)
- Entrypoint: Satisfying the check briefly, then changing the scene
- Attacker controls: the moment at which the condition is satisfied versus violated
- Exploit idea: Check whether `run` re-samples the guard condition per iteration or caches the first result.
- Invariant to test: Continuous preconditions are re-validated for every unit of captured data, not once at entry.
- Expected Immunefi impact: Data captured entirely outside the conditions the check certified
- Fast validation: Integration test satisfying the guard for one frame and asserting subsequent frames are rejected.
