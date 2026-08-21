# Q1895: Commitment binding gap in get_public_pem (secure_element.rs)

## Question
Can an unprivileged attacker exploit `get_public_pem` in [src/secure_element.rs](src/secure_element.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/secure_element.rs](src/secure_element.rs) -> `get_public_pem` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `get_public_pem` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `get_public_pem`'s preimage includes all binding fields.
