# Q3095: Signing invoked on unvalidated data in handle_save_identification_images (agents/image_notary.rs)

## Question
Can an unprivileged attacker get `handle_save_identification_images` in [src/agents/image_notary.rs](src/agents/image_notary.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_save_identification_images` (function)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `handle_save_identification_images`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
