# Q0791: Signature covers less than the security-relevant data in deserialize (wld-data-id/s3_region.rs)

## Question
Can an unprivileged attacker modify or influence a field that `deserialize` in [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) -> `deserialize` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `deserialize`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `deserialize` covers the full transmitted structure.
