# Q1024: Debug/telemetry artifact from sample_at_fps contains biometric or credential data (utils/mod.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `sample_at_fps` in [src/utils/mod.rs](src/utils/mod.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `sample_at_fps` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `sample_at_fps` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `sample_at_fps`'s artifact asserting no biometric or credential field is present.
