# Q1872: Signature covers less than the security-relevant data in make_tier2 (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker modify or influence a field that `make_tier2` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_tier2` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `make_tier2`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `make_tier2` covers the full transmitted structure.
