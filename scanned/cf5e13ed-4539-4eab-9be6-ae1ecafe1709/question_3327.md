# Q3327: Debug/telemetry artifact from ValueOffsetTimestamp contains biometric or credential data (debug_report.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `ValueOffsetTimestamp` in [src/debug_report.rs](src/debug_report.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `ValueOffsetTimestamp` (type)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `ValueOffsetTimestamp` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `ValueOffsetTimestamp`'s artifact asserting no biometric or credential field is present.
