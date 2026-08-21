# Q0988: Log record from init_datadog_client carries session-linkable biometric metadata (logger.rs)

## Question
Can an unprivileged attacker cause `init_datadog_client` in [src/logger.rs](src/logger.rs) to emit log/metric records that link identity to biometric measurements at a granularity that reconstructs another user's traits from routinely exported telemetry?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `init_datadog_client` (function)
- Entrypoint: Inducing the logging path during any session
- Attacker controls: conditions that maximize logged detail
- Exploit idea: Enumerate the fields `init_datadog_client` logs and assess re-identification potential.
- Invariant to test: Telemetry is aggregated and unlinkable; no per-user biometric measurement is exported.
- Expected Immunefi impact: Re-identifiable biometric metadata disclosed via telemetry
- Fast validation: Snapshot-test `init_datadog_client`'s emitted records asserting absence of linkable biometric fields.
