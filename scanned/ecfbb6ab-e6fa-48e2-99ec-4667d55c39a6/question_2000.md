# Q2000: TLS/authenticity of the request path in LocationData (backend/operator_status.rs)

## Question
Can an unprivileged attacker exploit `LocationData` in [src/backend/operator_status.rs](src/backend/operator_status.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/operator_status.rs](src/backend/operator_status.rs) -> `LocationData` (type)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `LocationData` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `LocationData` asserting scheme/host are invariant across all inputs.
