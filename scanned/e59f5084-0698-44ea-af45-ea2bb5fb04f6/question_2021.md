# Q2021: TLS/authenticity of the request path in TieredPackageRequest (backend/presigned_url.rs)

## Question
Can an unprivileged attacker exploit `TieredPackageRequest` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `TieredPackageRequest` (type)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `TieredPackageRequest` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `TieredPackageRequest` asserting scheme/host are invariant across all inputs.
