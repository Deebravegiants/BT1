# Q3351: Log record from Stats carries session-linkable biometric metadata (ssd.rs)

## Question
Can an unprivileged attacker cause `Stats` in [src/ssd.rs](src/ssd.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `Stats` (type)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `Stats` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `Stats`'s emitted records asserting absence of linkable biometric fields.
