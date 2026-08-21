# Q3371: Cleanup ordering in spawn_named_thread (utils/mod.rs)

## Question
Can an unprivileged attacker exploit `spawn_named_thread` in [src/utils/mod.rs](src/utils/mod.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `spawn_named_thread` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `spawn_named_thread`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `spawn_named_thread` at each step and asserting one-location invariance.
