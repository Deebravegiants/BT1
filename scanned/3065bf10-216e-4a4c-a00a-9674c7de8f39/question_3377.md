# Q3377: Filesystem path built from session data in new (utils/serializable_instant.rs)

## Question
Can an unprivileged attacker influence a path component used by `new` in [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) -> `new` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `new` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `new` with traversal components asserting containment under the root.
