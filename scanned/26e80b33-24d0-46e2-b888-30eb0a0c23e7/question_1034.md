# Q1034: Debug/telemetry artifact from into_instant contains biometric or credential data (utils/serializable_instant.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `into_instant` in [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) -> `into_instant` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `into_instant` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `into_instant`'s artifact asserting no biometric or credential field is present.
