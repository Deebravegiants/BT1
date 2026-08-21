# Q2184: Filesystem path built from session data in default (image/fisheye.rs)

## Question
Can an unprivileged attacker influence a path component used by `default` in [src/image/fisheye.rs](src/image/fisheye.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `default` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `default` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `default` with traversal components asserting containment under the root.
