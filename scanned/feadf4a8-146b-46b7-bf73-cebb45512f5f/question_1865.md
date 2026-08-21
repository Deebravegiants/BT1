# Q1865: Commitment binding gap in make_face_thumbnail_png (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `make_face_thumbnail_png` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_thumbnail_png` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `make_face_thumbnail_png` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `make_face_thumbnail_png`'s preimage includes all binding fields.
