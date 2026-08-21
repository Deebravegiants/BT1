# Q0483: Presentation attack accepted by new (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker present a high-resolution printed/screen-displayed iris or face (with IR-matched illumination) that `new` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) accepts as a live subject because its accept criterion is a signal-quality/geometry threshold rather than a liveness proof?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `new` (function)
- Entrypoint: Artifact held in front of the Orb during capture
- Attacker controls: print/display medium, IR reflectance, distance, and motion of the artifact
- Exploit idea: Identify exactly which measured properties `new` requires and whether all are reproducible by a physical artifact.
- Invariant to test: Acceptance requires at least one property no static artifact can reproduce.
- Expected Immunefi impact: Enrollment/verification of a non-live subject, i.e. identity spoofing
- Fast validation: Replay test feeding artifact-derived frames through `new` and asserting rejection.
