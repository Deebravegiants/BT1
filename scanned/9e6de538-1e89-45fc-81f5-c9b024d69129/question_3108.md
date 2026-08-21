# Q3108: TLS/authenticity of the request path in ensure_enough_space (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `ensure_enough_space` in [src/agents/image_notary.rs](src/agents/image_notary.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `ensure_enough_space` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `ensure_enough_space` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `ensure_enough_space` asserting scheme/host are invariant across all inputs.
