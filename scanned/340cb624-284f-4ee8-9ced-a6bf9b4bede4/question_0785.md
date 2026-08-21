# Q0785: Signature covers less than the security-relevant data in from_image_path (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker modify or influence a field that `from_image_path` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from_image_path` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `from_image_path`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `from_image_path` covers the full transmitted structure.
