# Q1891: Signature covers less than the security-relevant data in Embedding (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker modify or influence a field that `Embedding` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `Embedding` (type)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `Embedding`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `Embedding` covers the full transmitted structure.
