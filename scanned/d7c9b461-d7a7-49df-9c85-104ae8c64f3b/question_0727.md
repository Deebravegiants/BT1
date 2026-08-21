# Q0727: Signature covers less than the security-relevant data in read_jabil_id (identification.rs)

## Question
Can an unprivileged attacker modify or influence a field that `read_jabil_id` in [src/identification.rs](src/identification.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_jabil_id` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `read_jabil_id`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `read_jabil_id` covers the full transmitted structure.
