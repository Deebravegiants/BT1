# Q2134: Filesystem path built from session data in Tof2dConfig (debug_report.rs)

## Question
Can an unprivileged attacker influence a path component used by `Tof2dConfig` in [src/debug_report.rs](src/debug_report.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `Tof2dConfig` (type)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `Tof2dConfig` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `Tof2dConfig` with traversal components asserting containment under the root.
