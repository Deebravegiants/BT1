# Q0796: TLS/authenticity of the request path in log_decoding_error (backend/mod.rs)

## Question
Can an unprivileged attacker exploit `log_decoding_error` in [src/backend/mod.rs](src/backend/mod.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/backend/mod.rs](src/backend/mod.rs) -> `log_decoding_error` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `log_decoding_error` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `log_decoding_error` asserting scheme/host are invariant across all inputs.
