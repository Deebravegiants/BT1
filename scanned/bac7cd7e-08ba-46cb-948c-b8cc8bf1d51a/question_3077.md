# Q3077: Signing invoked on unvalidated data in orb_os_version (identification.rs)

## Question
Can an unprivileged attacker get `orb_os_version` in [src/identification.rs](src/identification.rs) to sign or attest data that has not yet passed the fraud/quality gate, so an Orb signature exists for a capture the pipeline later rejects?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `orb_os_version` (function)
- Entrypoint: Capture designed to fail a late-stage check
- Attacker controls: which stage fails, and when relative to signing
- Exploit idea: Establish the order of the gate and the signing call in `orb_os_version`.
- Invariant to test: Nothing is signed before every gate for that data has passed.
- Expected Immunefi impact: Orb-signed attestation over a rejected/fraudulent capture
- Fast validation: Integration test failing a late gate and asserting no signature was produced.
