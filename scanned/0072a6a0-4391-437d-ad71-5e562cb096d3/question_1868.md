# Q1868: Signing invoked on unvalidated data in make_face_embeddings_json (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker get `make_face_embeddings_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_embeddings_json` (function)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `make_face_embeddings_json`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
