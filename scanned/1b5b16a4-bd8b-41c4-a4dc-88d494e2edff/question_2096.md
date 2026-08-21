# Q2096: Commitment binding gap in biometric_capture_gps_location (debug_report.rs)

## Question
Can an unprivileged attacker exploit `biometric_capture_gps_location` in [src/debug_report.rs](src/debug_report.rs) computing a commitment over the biometric data without binding it to the session, user identity, and Orb identity, so a valid commitment can be transplanted to a different signup?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `biometric_capture_gps_location` (function)
- Entrypoint: Their own signup, whose artifacts they can observe or reproduce
- Attacker controls: the association between commitment and session metadata
- Exploit idea: Check the committed preimage in `biometric_capture_gps_location` for session/user/orb binding.
- Invariant to test: Commitments are domain-separated and bound to session, subject, and device identity.
- Expected Immunefi impact: Biometric commitment replayed into another user's signup record
- Fast validation: Unit-test asserting `biometric_capture_gps_location`'s preimage includes all binding fields.
