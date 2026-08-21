# Q0005: Trust confusion between operator and user codes in new (qr_scan/mod.rs)

## Question
Can an unprivileged attacker present a payload that `new` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) classifies as a higher-trust code class (operator/provisioning) than it is, because classification is by shape/prefix rather than by verified authenticity?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `new` (function)
- Entrypoint: Scanned QR payload shaped like a higher-trust code
- Attacker controls: prefix, field layout, and length of the payload
- Exploit idea: Construct a payload that satisfies the discriminator used in `new` for the privileged branch.
- Invariant to test: Code class is decided by cryptographically verified authenticity, not by attacker-reproducible formatting.
- Expected Immunefi impact: Unprivileged attacker driving an operator/provisioning-only flow
- Fast validation: Unit-test `new` with a self-minted higher-trust-shaped payload and assert rejection.
