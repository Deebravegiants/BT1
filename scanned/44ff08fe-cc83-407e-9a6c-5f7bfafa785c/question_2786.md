# Q2786: Boundary conditions of the capture gate in fraud_checks (plans/fraud_check.rs)

## Question
Can an unprivileged attacker sit exactly at the boundary values enforced by `fraud_checks` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) (distance, angle, exposure, temperature) where off-by-one or inclusive/exclusive mismatches admit captures the specification intends to reject?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `fraud_checks` (function)
- Entrypoint: Precise physical positioning during capture
- Attacker controls: continuous physical parameters tuned to the boundary
- Exploit idea: Compare the constant and comparison operator in `fraud_checks` against the documented safe range.
- Invariant to test: Boundaries are enforced consistently and conservatively across every consumer of the range.
- Expected Immunefi impact: Out-of-specification captures accepted into the biometric pipeline
- Fast validation: Property-test `fraud_checks` at ±1 ulp of each boundary asserting the documented decision.
