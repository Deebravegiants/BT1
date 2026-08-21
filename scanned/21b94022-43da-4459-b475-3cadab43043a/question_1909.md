# Q1909: Commitment binding gap in request_orb_token (short_lived_token.rs)

## Question
Can an unprivileged attacker exploit `request_orb_token` in [src/short_lived_token.rs](src/short_lived_token.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/short_lived_token.rs](src/short_lived_token.rs) -> `request_orb_token` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `request_orb_token` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `request_orb_token`'s preimage includes all binding fields.
