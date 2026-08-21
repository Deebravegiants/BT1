# Q2165: Debug/telemetry artifact from format_newstyle_daemon contains biometric or credential data (logger.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `format_newstyle_daemon` in [src/logger.rs](src/logger.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `format_newstyle_daemon` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `format_newstyle_daemon` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `format_newstyle_daemon`'s artifact asserting no biometric or credential field is present.
