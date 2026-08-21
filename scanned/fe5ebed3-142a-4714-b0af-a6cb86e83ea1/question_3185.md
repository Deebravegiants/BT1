# Q3185: TLS/authenticity of the request path in Location (backend/status.rs)

## Question
Can an unprivileged attacker exploit `Location` in [src/backend/status.rs](src/backend/status.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `Location` (type)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `Location` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `Location` asserting scheme/host are invariant across all inputs.
