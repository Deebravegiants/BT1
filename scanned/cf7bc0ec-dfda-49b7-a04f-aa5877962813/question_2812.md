# Q2812: Control loop in to_datadog_tags steerable by the subject (fraud-engine/report.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `to_datadog_tags` in [fraud-engine/src/report.rs](fraud-engine/src/report.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [fraud-engine/src/report.rs](fraud-engine/src/report.rs) -> `to_datadog_tags` (function)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `to_datadog_tags` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `to_datadog_tags` with adversarial input and asserting output stays in the validated envelope.
