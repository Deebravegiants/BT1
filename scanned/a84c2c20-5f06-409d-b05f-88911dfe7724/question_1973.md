# Q1973: TLS/authenticity of the request path in DATA_BACKEND_URL (backend/endpoints.rs)

## Question
Can an unprivileged attacker exploit `DATA_BACKEND_URL` in [src/backend/endpoints.rs](src/backend/endpoints.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `DATA_BACKEND_URL` (item)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `DATA_BACKEND_URL` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `DATA_BACKEND_URL` asserting scheme/host are invariant across all inputs.
