# Q0498: Boundary conditions of the capture gate in take_log (agents/mirror.rs)

## Question
Can an unprivileged attacker sit exactly at the boundary values enforced by `take_log` in [src/agents/mirror.rs](src/agents/mirror.rs) (distance, angle, exposure, temperature) where off-by-one or inclusive/exclusive mismatches admit captures the specification intends to reject?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `take_log` (function)
- Entrypoint: Precise physical positioning during capture
- Attacker controls: continuous physical parameters tuned to the boundary
- Exploit idea: Compare the constant and comparison operator in `take_log` against the documented safe range.
- Invariant to test: Boundaries are enforced consistently and conservatively across every consumer of the range.
- Expected Immunefi impact: Out-of-specification captures accepted into the biometric pipeline
- Fast validation: Property-test `take_log` at ±1 ulp of each boundary asserting the documented decision.
