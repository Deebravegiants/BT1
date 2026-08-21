# Q1652: Boundary conditions of the capture gate in Agent (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker sit exactly at the boundary values enforced by `Agent` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) (distance, angle, exposure, temperature) where off-by-one or inclusive/exclusive mismatches admit captures the specification intends to reject?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `Agent` (type)
- Entrypoint: Precise physical positioning during capture
- Attacker controls: continuous physical parameters tuned to the boundary
- Exploit idea: Compare the constant and comparison operator in `Agent` against the documented safe range.
- Invariant to test: Boundaries are enforced consistently and conservatively across every consumer of the range.
- Expected Immunefi impact: Out-of-specification captures accepted into the biometric pipeline
- Fast validation: Property-test `Agent` at ±1 ulp of each boundary asserting the documented decision.
