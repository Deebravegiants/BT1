# Q0806: TLS/authenticity of the request path in to_screaming_snake_case (backend/signup_post.rs)

## Question
Can an unprivileged attacker exploit `to_screaming_snake_case` in [src/backend/signup_post.rs](src/backend/signup_post.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `to_screaming_snake_case` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `to_screaming_snake_case` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `to_screaming_snake_case` asserting scheme/host are invariant across all inputs.
