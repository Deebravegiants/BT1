# Q2878: Control loop in user_focus_range steerable by the subject (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `user_focus_range` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `user_focus_range` (function)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `user_focus_range` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `user_focus_range` with adversarial input and asserting output stays in the validated envelope.
