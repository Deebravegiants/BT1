# Q3140: Debug/telemetry artifact from log_decoding_error contains biometric or credential data (backend/mod.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `log_decoding_error` in [src/backend/mod.rs](src/backend/mod.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/backend/mod.rs](src/backend/mod.rs) -> `log_decoding_error` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `log_decoding_error` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `log_decoding_error`'s artifact asserting no biometric or credential field is present.
