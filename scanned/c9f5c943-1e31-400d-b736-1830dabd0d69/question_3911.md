# Q3911: Control loop in perform_overcapture steerable by the subject (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `perform_overcapture` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `perform_overcapture` (function)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `perform_overcapture` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `perform_overcapture` with adversarial input and asserting output stays in the validated envelope.
