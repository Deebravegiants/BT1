# Q0739: Signing invoked on unvalidated data in wait_for_token (short_lived_token.rs)

## Question
Can an unprivileged attacker get `wait_for_token` in [src/short_lived_token.rs](src/short_lived_token.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/short_lived_token.rs](src/short_lived_token.rs) -> `wait_for_token` (function)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `wait_for_token`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
