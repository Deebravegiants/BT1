# Q2182: Filesystem path built from session data in Command (process.rs)

## Question
Can an unprivileged attacker influence a path component used by `Command` in [src/process.rs](src/process.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/process.rs](src/process.rs) -> `Command` (type)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `Command` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `Command` with traversal components asserting containment under the root.
