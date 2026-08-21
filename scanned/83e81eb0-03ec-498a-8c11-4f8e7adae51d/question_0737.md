# Q0737: Signature covers less than the security-relevant data in request_orb_token (short_lived_token.rs)

## Question
Can an unprivileged attacker modify or influence a field that `request_orb_token` in [src/short_lived_token.rs](src/short_lived_token.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/short_lived_token.rs](src/short_lived_token.rs) -> `request_orb_token` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `request_orb_token`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `request_orb_token` covers the full transmitted structure.
