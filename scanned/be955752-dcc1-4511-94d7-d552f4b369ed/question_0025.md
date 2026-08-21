# Q0025: Trust confusion between operator and user codes in exit_strategy (agents/qr_code.rs)

## Question
Can an unprivileged attacker present a payload that `exit_strategy` in [src/agents/qr_code.rs](src/agents/qr_code.rs) classifies as a higher-trust code class (operator/provisioning) than it is, because classification is by shape/prefix rather than by verified authenticity?

## Target
- File/function: [src/agents/qr_code.rs](src/agents/qr_code.rs) -> `exit_strategy` (function)
- Entrypoint: Scanned QR payload shaped like a higher-trust code
- Attacker controls: prefix, field layout, and length of the payload
- Exploit idea: Construct a payload that satisfies the discriminator used in `exit_strategy` for the privileged branch.
- Invariant to test: Code class is decided by cryptographically verified authenticity, not by attacker-reproducible formatting.
- Expected Immunefi impact: Unprivileged attacker driving an operator/provisioning-only flow
- Fast validation: Unit-test `exit_strategy` with a self-minted higher-trust-shaped payload and assert rejection.
