# Q3216: Cleanup ordering in Config (config.rs)

## Question
Can an unprivileged attacker exploit `Config` in [src/config.rs](src/config.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/config.rs](src/config.rs) -> `Config` (type)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `Config`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `Config` at each step and asserting one-location invariance.
