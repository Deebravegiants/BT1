# Q0650: Control loop in EstimatePredictionBboxOutput steerable by the subject (python/rgb_net.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `EstimatePredictionBboxOutput` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `EstimatePredictionBboxOutput` (type)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `EstimatePredictionBboxOutput` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `EstimatePredictionBboxOutput` with adversarial input and asserting output stays in the validated envelope.
