# Q1928: Commitment binding gap in handle_save_thermal_data (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `handle_save_thermal_data` in [src/agents/image_notary.rs](src/agents/image_notary.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_save_thermal_data` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `handle_save_thermal_data` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `handle_save_thermal_data`'s preimage includes all binding fields.
