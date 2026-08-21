# Q3860: Control loop in handle_ir_eye_camera steerable by the subject (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker steer the feedback loop implemented in `handle_ir_eye_camera` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) (autofocus, exposure, mirror, PID) with adversarial motion or reflectance so it settles on a configuration that systematically degrades the evidence anti-fraud checks depend on?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `handle_ir_eye_camera` (function)
- Entrypoint: Adversarial motion/reflectance during capture
- Attacker controls: physical motion profile and surface reflectance presented to the sensor
- Exploit idea: Check whether `handle_ir_eye_camera` clamps its output and whether downstream checks are validated at the clamped extremes.
- Invariant to test: Control outputs are clamped to a range in which every downstream check remains valid.
- Expected Immunefi impact: Anti-fraud evidence degraded to the point of bypass
- Fast validation: Simulation test driving `handle_ir_eye_camera` with adversarial input and asserting output stays in the validated envelope.
