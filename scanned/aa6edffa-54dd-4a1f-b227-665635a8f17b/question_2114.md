# Q2114: Filesystem path built from session data in SignupStatus (debug_report.rs)

## Question
Can an unprivileged attacker influence a path component used by `SignupStatus` in [src/debug_report.rs](src/debug_report.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `SignupStatus` (type)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `SignupStatus` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `SignupStatus` with traversal components asserting containment under the root.
