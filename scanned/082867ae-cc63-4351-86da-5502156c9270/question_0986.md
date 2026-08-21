# Q0986: Filesystem path built from session data in try_create_datadog_client_from_socket (logger.rs)

## Question
Can an unprivileged attacker influence a path component used by `try_create_datadog_client_from_socket` in [src/logger.rs](src/logger.rs) (identity, session, image name) so writes escape the intended directory or collide with another session's files?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `try_create_datadog_client_from_socket` (function)
- Entrypoint: Identity/session fields from the scanned payload
- Attacker controls: path-component strings including separators and traversal sequences
- Exploit idea: Check `try_create_datadog_client_from_socket` for component validation and canonicalization before joining.
- Invariant to test: Paths are built only from validated, separator-free components under a fixed root.
- Expected Immunefi impact: Cross-session file overwrite or write outside the intended storage root
- Fast validation: Unit-test `try_create_datadog_client_from_socket` with traversal components asserting containment under the root.
