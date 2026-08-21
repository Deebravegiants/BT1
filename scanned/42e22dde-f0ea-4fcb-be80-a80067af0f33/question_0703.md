# Q0703: TLS/authenticity of the request path in compute_hyrax_commitment (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `compute_hyrax_commitment` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `compute_hyrax_commitment` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `compute_hyrax_commitment` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `compute_hyrax_commitment` asserting scheme/host are invariant across all inputs.
