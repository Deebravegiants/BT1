# Q0917: Signature covers less than the security-relevant data in fraud_check_feedback_messages (debug_report.rs)

## Question
Can an unprivileged attacker modify or influence a field that `fraud_check_feedback_messages` in [src/debug_report.rs](src/debug_report.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `fraud_check_feedback_messages` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `fraud_check_feedback_messages`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `fraud_check_feedback_messages` covers the full transmitted structure.
