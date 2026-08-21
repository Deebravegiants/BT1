# Q3234: Commitment binding gap in Queue (agents/data_uploader.rs)

## Question
Can an unprivileged attacker exploit `Queue` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `Queue` (type)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `Queue` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `Queue`'s preimage includes all binding fields.
