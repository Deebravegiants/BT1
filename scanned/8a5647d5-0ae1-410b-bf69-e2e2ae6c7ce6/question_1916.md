# Q1916: Commitment binding gap in default (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `default` in [src/agents/image_notary.rs](src/agents/image_notary.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `default` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `default` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `default`'s preimage includes all binding fields.
