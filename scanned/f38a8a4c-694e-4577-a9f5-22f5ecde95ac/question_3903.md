# Q3903: Boundary conditions of the capture gate in perform_multi_wavelength (biometric_capture/multi_wavelength.rs)

## Question
Can an unprivileged attacker sit exactly at the boundary values enforced by `perform_multi_wavelength` in [src/plans/biometric_capture/multi_wavelength.rs](src/plans/biometric_capture/multi_wavelength.rs) (distance, angle, exposure, temperature) where off-by-one or inclusive/exclusive mismatches admit captures the specification intends to reject?

## Target
- File/function: [src/plans/biometric_capture/multi_wavelength.rs](src/plans/biometric_capture/multi_wavelength.rs) -> `perform_multi_wavelength` (function)
- Entrypoint: Precise physical positioning during capture
- Attacker controls: continuous physical parameters tuned to the boundary
- Exploit idea: Compare the constant and comparison operator in `perform_multi_wavelength` against the documented safe range.
- Invariant to test: Boundaries are enforced consistently and conservatively across every consumer of the range.
- Expected Immunefi impact: Out-of-specification captures accepted into the biometric pipeline
- Fast validation: Property-test `perform_multi_wavelength` at ±1 ulp of each boundary asserting the documented decision.
