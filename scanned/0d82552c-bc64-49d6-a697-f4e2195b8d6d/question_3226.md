# Q3226: Filesystem path built from session data in push (agents/data_uploader.rs)

## Question
Can an unprivileged attacker influence a path component used by `push` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `push` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `push` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `push` with traversal components asserting containment under the root.
