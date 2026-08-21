# Q2195: Cleanup ordering in ip_geo_info (utils/mod.rs)

## Question
Can an unprivileged attacker exploit `ip_geo_info` in [src/utils/mod.rs](src/utils/mod.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `ip_geo_info` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `ip_geo_info`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `ip_geo_info` at each step and asserting one-location invariance.
