# Q1033: Log record from new carries session-linkable biometric metadata (utils/serializable_instant.rs)

## Question
Can an unprivileged attacker cause `new` in [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) -> `new` (function)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `new` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `new`'s emitted records asserting absence of linkable biometric fields.
