# Q2063: Debug/telemetry artifact from run contains biometric or credential data (agents/image_uploader.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `run` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `run` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `run` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `run`'s artifact asserting no biometric or credential field is present.
