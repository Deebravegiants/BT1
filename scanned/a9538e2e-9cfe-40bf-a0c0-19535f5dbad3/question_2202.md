# Q2202: Cleanup ordering in into_ndarray (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker exploit `into_ndarray` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `into_ndarray` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `into_ndarray`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `into_ndarray` at each step and asserting one-location invariance.
