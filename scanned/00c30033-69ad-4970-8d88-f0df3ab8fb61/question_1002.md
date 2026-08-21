# Q1002: Cleanup ordering in perform_async (ssd.rs)

## Question
Can an unprivileged attacker exploit `perform_async` in [src/ssd.rs](src/ssd.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `perform_async` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `perform_async`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `perform_async` at each step and asserting one-location invariance.
