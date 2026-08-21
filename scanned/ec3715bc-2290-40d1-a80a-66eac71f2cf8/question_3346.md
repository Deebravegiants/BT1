# Q3346: Debug/telemetry artifact from perform_async contains biometric or credential data (ssd.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `perform_async` in [src/ssd.rs](src/ssd.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `perform_async` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `perform_async` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `perform_async`'s artifact asserting no biometric or credential field is present.
