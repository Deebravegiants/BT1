# Q3358: Log record from undistort_coordinates carries session-linkable biometric metadata (image/fisheye.rs)

## Question
Can an unprivileged attacker cause `undistort_coordinates` in [src/image/fisheye.rs](src/image/fisheye.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `undistort_coordinates` (function)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `undistort_coordinates` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `undistort_coordinates`'s emitted records asserting absence of linkable biometric fields.
