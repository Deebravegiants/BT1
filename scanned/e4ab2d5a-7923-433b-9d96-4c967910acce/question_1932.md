# Q1932: TLS/authenticity of the request path in save_frame_with_id (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `save_frame_with_id` in [src/agents/image_notary.rs](src/agents/image_notary.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_frame_with_id` (function)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `save_frame_with_id` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `save_frame_with_id` asserting scheme/host are invariant across all inputs.
