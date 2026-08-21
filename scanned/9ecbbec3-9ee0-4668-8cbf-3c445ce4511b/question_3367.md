# Q3367: Debug/telemetry artifact from ip_geo_info contains biometric or credential data (utils/mod.rs)

## Question
Can an unprivileged attacker trigger the artifact-generation path in `ip_geo_info` in [src/utils/mod.rs](src/utils/mod.rs) so the emitted report/telemetry embeds raw frames, iris codes, identity tokens, or network credentials rather than redacted summaries?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `ip_geo_info` (function)
- Entrypoint: Inducing the error/report condition during their own signup
- Attacker controls: conditions that reliably trigger report generation
- Exploit idea: Enumerate the fields serialized by `ip_geo_info` for biometric or credential content.
- Invariant to test: Diagnostic artifacts contain no raw biometric or credential material.
- Expected Immunefi impact: Disclosure of biometric/credential data through diagnostic artifacts
- Fast validation: Snapshot-test `ip_geo_info`'s artifact asserting no biometric or credential field is present.
