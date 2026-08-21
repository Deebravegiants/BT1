# Q3120: Signing invoked on unvalidated data in Output (agents/image_notary.rs)

## Question
Can an unprivileged attacker get `Output` in [src/agents/image_notary.rs](src/agents/image_notary.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `Output` (type)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `Output`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
