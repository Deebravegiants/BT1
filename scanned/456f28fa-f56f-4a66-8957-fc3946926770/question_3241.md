# Q3241: Filesystem path built from session data in log_data_to_upload_left (agents/image_uploader.rs)

## Question
Can an unprivileged attacker influence a path component used by `log_data_to_upload_left` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `log_data_to_upload_left` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `log_data_to_upload_left` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `log_data_to_upload_left` with traversal components asserting containment under the root.
