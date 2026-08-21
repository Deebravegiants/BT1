# Q3132: Commitment binding gap in ImageId (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker exploit `ImageId` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `ImageId` (type)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `ImageId` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `ImageId`'s preimage includes all binding fields.
