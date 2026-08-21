# Q0999: Filesystem path built from session data in stats (ssd.rs)

## Question
Can an unprivileged attacker influence a path component used by `stats` in [src/ssd.rs](src/ssd.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/ssd.rs](src/ssd.rs) -> `stats` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `stats` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `stats` with traversal components asserting containment under the root.
