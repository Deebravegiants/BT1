# Q0973: Package version/downgrade selection in CommonCameraExecutionTimestamp (debug_report.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `CommonCameraExecutionTimestamp` in [src/debug_report.rs](src/debug_report.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `CommonCameraExecutionTimestamp` (type)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `CommonCameraExecutionTimestamp` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `CommonCameraExecutionTimestamp` with a downgrade-shaped input asserting the strong format is used.
