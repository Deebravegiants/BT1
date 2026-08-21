# Q1946: TLS/authenticity of the request path in SaveThermalDataInput (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `SaveThermalDataInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveThermalDataInput` (type)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `SaveThermalDataInput` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `SaveThermalDataInput` asserting scheme/host are invariant across all inputs.
