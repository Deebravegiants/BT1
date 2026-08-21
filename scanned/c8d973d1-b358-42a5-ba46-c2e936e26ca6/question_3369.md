# Q3369: Log record from log_iris_data carries session-linkable biometric metadata (utils/mod.rs)

## Question
Can an unprivileged attacker cause `log_iris_data` in [src/utils/mod.rs](src/utils/mod.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `log_iris_data` (function)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `log_iris_data` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `log_iris_data`'s emitted records asserting absence of linkable biometric fields.
