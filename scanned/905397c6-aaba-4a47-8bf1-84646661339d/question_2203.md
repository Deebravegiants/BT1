# Q2203: Filesystem path built from session data in as_ndarray (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker influence a path component used by `as_ndarray` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `as_ndarray` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `as_ndarray` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `as_ndarray` with traversal components asserting containment under the root.
