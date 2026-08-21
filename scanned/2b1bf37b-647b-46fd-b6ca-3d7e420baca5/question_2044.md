# Q2044: Filesystem path built from session data in Config (config.rs)

## Question
Can an unprivileged attacker influence a path component used by `Config` in [src/config.rs](src/config.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/config.rs](src/config.rs) -> `Config` (type)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `Config` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `Config` with traversal components asserting containment under the root.
