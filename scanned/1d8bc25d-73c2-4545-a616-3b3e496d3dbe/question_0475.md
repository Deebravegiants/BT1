# Q0475: Control loop in calculate_mirror_point steerable by the subject (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `calculate_mirror_point` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `calculate_mirror_point` (function)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `calculate_mirror_point` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `calculate_mirror_point` with adversarial input and asserting output stays in the validated envelope.
