# Q1338: Guard evaluated once but relied on continuously in handle_rgb_net (brokers/orb.rs)

## Question
Can an unprivileged attacker satisfy a condition once at the entry of `handle_rgb_net` in [src/brokers/orb.rs](src/brokers/orb.rs) (presence, distance, verdict) and then violate it for the remainder of the stage, since the guard is not re-evaluated?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `handle_rgb_net` (function)
- Entrypoint: Satisfying the check briefly, then changing the scene
- Attacker controls: the moment at which the condition is satisfied versus violated
- Exploit idea: Check whether `handle_rgb_net` re-samples the guard condition per iteration or caches the first result.
- Invariant to test: Continuous preconditions are re-validated for every unit of captured data, not once at entry.
- Expected Immunefi impact: Data captured entirely outside the conditions the check certified
- Fast validation: Integration test satisfying the guard for one frame and asserting subsequent frames are rejected.
