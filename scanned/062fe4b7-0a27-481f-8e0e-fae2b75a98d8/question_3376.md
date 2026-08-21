# Q3376: Cleanup ordering in RkyvNdarray (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker exploit `RkyvNdarray` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `RkyvNdarray` (type)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `RkyvNdarray`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `RkyvNdarray` at each step and asserting one-location invariance.
