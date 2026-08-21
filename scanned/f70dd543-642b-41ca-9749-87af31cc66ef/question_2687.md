# Q2687: Boundary conditions of the capture gate in handle_ir_auto_focus (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker sit exactly at the boundary values enforced by `handle_ir_auto_focus` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) (distance, angle, exposure, temperature) where off-by-one or inclusive/exclusive mismatches admit captures the specification intends to reject?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `handle_ir_auto_focus` (function)
- Entrypoint: Precise physical positioning during capture
- Attacker controls: continuous physical parameters tuned to the boundary
- Exploit idea: Compare the constant and comparison operator in `handle_ir_auto_focus` against the documented safe range.
- Invariant to test: Boundaries are enforced consistently and conservatively across every consumer of the range.
- Expected Immunefi impact: Out-of-specification captures accepted into the biometric pipeline
- Fast validation: Property-test `handle_ir_auto_focus` at ±1 ulp of each boundary asserting the documented decision.
