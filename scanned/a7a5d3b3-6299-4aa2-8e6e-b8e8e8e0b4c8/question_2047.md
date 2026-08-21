# Q2047: TLS/authenticity of the request path in from (calibration.rs)

## Question
Can an unprivileged attacker exploit `from` in [src/calibration.rs](src/calibration.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/calibration.rs](src/calibration.rs) -> `from` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `from` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `from` asserting scheme/host are invariant across all inputs.
