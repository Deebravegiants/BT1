# Q3382: Signature covers less than the security-relevant data in SerializeWithSortedKeys (utils/serialize_with_sorted_keys.rs)

## Question
Can an unprivileged attacker modify or influence a field that `SerializeWithSortedKeys` in [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) -> `SerializeWithSortedKeys` (type)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `SerializeWithSortedKeys`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `SerializeWithSortedKeys` covers the full transmitted structure.
