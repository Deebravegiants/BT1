# Q3163: TLS/authenticity of the request path in do_request (backend/user_status.rs)

## Question
Can an unprivileged attacker exploit `do_request` in [src/backend/user_status.rs](src/backend/user_status.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/user_status.rs](src/backend/user_status.rs) -> `do_request` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `do_request` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `do_request` asserting scheme/host are invariant across all inputs.
