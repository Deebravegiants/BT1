# Q3318: Signing invoked on unvalidated data in FaceIdentifierIsValidMetadata (debug_report.rs)

## Question
Can an unprivileged attacker get `FaceIdentifierIsValidMetadata` in [src/debug_report.rs](src/debug_report.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `FaceIdentifierIsValidMetadata` (type)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `FaceIdentifierIsValidMetadata`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
