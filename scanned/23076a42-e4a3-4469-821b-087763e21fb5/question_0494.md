# Q0494: Control loop in Agent steerable by the subject (agents/distance.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `Agent` in [src/agents/distance.rs](src/agents/distance.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/agents/distance.rs](src/agents/distance.rs) -> `Agent` (type)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `Agent` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `Agent` with adversarial input and asserting output stays in the validated envelope.
