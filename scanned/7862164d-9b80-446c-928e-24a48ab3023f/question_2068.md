# Q2068: Commitment binding gap in get_signup_paths (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit `get_signup_paths` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `get_signup_paths` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `get_signup_paths` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `get_signup_paths`'s preimage includes all binding fields.
