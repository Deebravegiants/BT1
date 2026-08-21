# Q3373: Filesystem path built from session data in from (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker influence a path component used by `from` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `from` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `from` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `from` with traversal components asserting containment under the root.
