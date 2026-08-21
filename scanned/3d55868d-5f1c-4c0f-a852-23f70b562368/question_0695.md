# Q0695: Signature covers less than the security-relevant data in salted_sha256 (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker modify or influence a field that `salted_sha256` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `salted_sha256` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `salted_sha256`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `salted_sha256` covers the full transmitted structure.
