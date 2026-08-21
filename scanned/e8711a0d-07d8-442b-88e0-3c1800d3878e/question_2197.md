# Q2197: Filesystem path built from session data in log_iris_data (utils/mod.rs)

## Question
Can an unprivileged attacker influence a path component used by `log_iris_data` in [src/utils/mod.rs](src/utils/mod.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `log_iris_data` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `log_iris_data` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `log_iris_data` with traversal components asserting containment under the root.
