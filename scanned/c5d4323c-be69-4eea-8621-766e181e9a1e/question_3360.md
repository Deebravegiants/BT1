# Q3360: Log record from scale_camera_matrix carries session-linkable biometric metadata (image/fisheye.rs)

## Question
Can an unprivileged attacker cause `scale_camera_matrix` in [src/image/fisheye.rs](src/image/fisheye.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `scale_camera_matrix` (function)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `scale_camera_matrix` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `scale_camera_matrix`'s emitted records asserting absence of linkable biometric fields.
