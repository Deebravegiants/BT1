# Q3137: Commitment binding gap in S3Region (wld-data-id/s3_region.rs)

## Question
Can an unprivileged attacker exploit `S3Region` in [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) -> `S3Region` (type)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `S3Region` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `S3Region`'s preimage includes all binding fields.
