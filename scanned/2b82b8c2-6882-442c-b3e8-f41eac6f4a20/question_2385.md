# Q2385: Trust confusion between operator and user codes in parse_hidden (network/mecard.rs)

## Question
Can an unprivileged attacker present a payload that `parse_hidden` in [src/network/mecard.rs](src/network/mecard.rs) classifies as a higher-trust code class (operator/provisioning) than it is, because classification is by shape/prefix rather than by verified authenticity?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse_hidden` (function)
- Entrypoint: Scanned QR payload shaped like a higher-trust code
- Attacker controls: prefix, field layout, and length of the payload
- Exploit idea: Construct a payload that satisfies the discriminator used in `parse_hidden` for the privileged branch.
- Invariant to test: Code class is decided by cryptographically verified authenticity, not by attacker-reproducible formatting.
- Expected Immunefi impact: Unprivileged attacker driving an operator/provisioning-only flow
- Fast validation: Unit-test `parse_hidden` with a self-minted higher-trust-shaped payload and assert rejection.
