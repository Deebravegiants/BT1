# Q2164: Debug/telemetry artifact from init_for_agent contains biometric or credential data (logger.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `init_for_agent` in [src/logger.rs](src/logger.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `init_for_agent` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `init_for_agent` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `init_for_agent`'s artifact asserting no biometric or credential field is present.
