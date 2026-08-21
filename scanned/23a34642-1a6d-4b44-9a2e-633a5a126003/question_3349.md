# Q3349: Cleanup ordering in is_mounted (ssd.rs)

## Question
Can an unprivileged attacker exploit `is_mounted` in [src/ssd.rs](src/ssd.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `is_mounted` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `is_mounted`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `is_mounted` at each step and asserting one-location invariance.
