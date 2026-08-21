# Q3566: Trust confusion between operator and user codes in Opt (wpa-supplicant-interface/main.rs)

## Question
Can an unprivileged attacker present a payload that `Opt` in [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) classifies as a higher-trust code class (operator/provisioning) than it is, because classification is by shape/prefix rather than by verified authenticity?

## Target
- File/function: [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) -> `Opt` (type)
- Entrypoint: Scanned QR payload shaped like a higher-trust code
- Attacker controls: prefix, field layout, and length of the payload
- Exploit idea: Construct a payload that satisfies the discriminator used in `Opt` for the privileged branch.
- Invariant to test: Code class is decided by cryptographically verified authenticity, not by attacker-reproducible formatting.
- Expected Immunefi impact: Unprivileged attacker driving an operator/provisioning-only flow
- Fast validation: Unit-test `Opt` with a self-minted higher-trust-shaped payload and assert rejection.
