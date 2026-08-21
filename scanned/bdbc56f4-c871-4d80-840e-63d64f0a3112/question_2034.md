# Q2034: Debug/telemetry artifact from store contains biometric or credential data (config.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `store` in [src/config.rs](src/config.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/config.rs](src/config.rs) -> `store` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `store` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `store`'s artifact asserting no biometric or credential field is present.
