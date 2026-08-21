# Q2151: Debug/telemetry artifact from ThermalCameraMetadata contains biometric or credential data (debug_report.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `ThermalCameraMetadata` in [src/debug_report.rs](src/debug_report.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `ThermalCameraMetadata` (type)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `ThermalCameraMetadata` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `ThermalCameraMetadata`'s artifact asserting no biometric or credential field is present.
