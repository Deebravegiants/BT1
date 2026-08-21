# Q1516: Presentation attack accepted by handle_ir_eye_camera (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker present a high-resolution printed/screen-displayed iris or face (with IR-matched illumination) that `handle_ir_eye_camera` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) accepts as a live subject because its accept criterion is a signal-quality/geometry threshold rather than a liveness proof?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `handle_ir_eye_camera` (function)
- Entrypoint: Artifact held in front of the Orb during capture
- Attacker controls: print/display medium, IR reflectance, distance, and motion of the artifact
- Exploit idea: Identify exactly which measured properties `handle_ir_eye_camera` requires and whether all are reproducible by a physical artifact.
- Invariant to test: Acceptance requires at least one property no static artifact can reproduce.
- Expected Immunefi impact: Enrollment/verification of a non-live subject, i.e. identity spoofing
- Fast validation: Replay test feeding artifact-derived frames through `handle_ir_eye_camera` and asserting rejection.
