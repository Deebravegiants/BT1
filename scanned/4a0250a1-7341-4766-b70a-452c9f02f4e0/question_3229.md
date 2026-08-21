# Q3229: Cleanup ordering in drop_oldest (agents/data_uploader.rs)

## Question
Can an unprivileged attacker exploit `drop_oldest` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `drop_oldest` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `drop_oldest`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `drop_oldest` at each step and asserting one-location invariance.
