# Q3362: Filesystem path built from session data in make_camera_matrix (image/fisheye.rs)

## Question
Can an unprivileged attacker influence a path component used by `make_camera_matrix` in [src/image/fisheye.rs](src/image/fisheye.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `make_camera_matrix` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `make_camera_matrix` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `make_camera_matrix` with traversal components asserting containment under the root.
