# Q3303: Cleanup ordering in RgbCameraConfig (debug_report.rs)

## Question
Can an unprivileged attacker exploit `RgbCameraConfig` in [src/debug_report.rs](src/debug_report.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `RgbCameraConfig` (type)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `RgbCameraConfig`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `RgbCameraConfig` at each step and asserting one-location invariance.
