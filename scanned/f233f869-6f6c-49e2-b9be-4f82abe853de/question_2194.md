# Q2194: Cleanup ordering in Calibration (image/fisheye.rs)

## Question
Can an unprivileged attacker exploit `Calibration` in [src/image/fisheye.rs](src/image/fisheye.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `Calibration` (type)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `Calibration`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `Calibration` at each step and asserting one-location invariance.
