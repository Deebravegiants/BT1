# Q3320: Commitment binding gap in IrNetMetadata (debug_report.rs)

## Question
Can an unprivileged attacker exploit `IrNetMetadata` in [src/debug_report.rs](src/debug_report.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `IrNetMetadata` (type)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `IrNetMetadata` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `IrNetMetadata`'s preimage includes all binding fields.
