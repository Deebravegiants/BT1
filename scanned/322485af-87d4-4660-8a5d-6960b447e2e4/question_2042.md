# Q2042: Filesystem path built from session data in config_file_path (config.rs)

## Question
Can an unprivileged attacker influence a path component used by `config_file_path` in [src/config.rs](src/config.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/config.rs](src/config.rs) -> `config_file_path` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `config_file_path` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `config_file_path` with traversal components asserting containment under the root.
