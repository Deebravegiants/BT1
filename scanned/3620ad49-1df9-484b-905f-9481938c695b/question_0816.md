# Q0816: TLS/authenticity of the request path in empty_string_is_none (backend/signup_poll.rs)

## Question
Can an unprivileged attacker exploit `empty_string_is_none` in [src/backend/signup_poll.rs](src/backend/signup_poll.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/signup_poll.rs](src/backend/signup_poll.rs) -> `empty_string_is_none` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `empty_string_is_none` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `empty_string_is_none` asserting scheme/host are invariant across all inputs.
