# Q0066: Guard evaluated once but relied on continuously in skip_pipeline (plans/mod.rs)

## Question
Can an unprivileged attacker satisfy a condition once at the entry of `skip_pipeline` in [src/plans/mod.rs](src/plans/mod.rs) (presence, distance, verdict) and then violate it for the remainder of the stage, since the guard is not re-evaluated?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `skip_pipeline` (function)
- Entrypoint: Satisfying the check briefly, then changing the scene
- Attacker controls: the moment at which the condition is satisfied versus violated
- Exploit idea: Check whether `skip_pipeline` re-samples the guard condition per iteration or caches the first result.
- Invariant to test: Continuous preconditions are re-validated for every unit of captured data, not once at entry.
- Expected Immunefi impact: Data captured entirely outside the conditions the check certified
- Fast validation: Integration test satisfying the guard for one frame and asserting subsequent frames are rejected.
