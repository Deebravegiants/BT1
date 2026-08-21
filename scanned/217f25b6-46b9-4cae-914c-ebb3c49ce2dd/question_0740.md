# Q0740: Signature covers less than the security-relevant data in signup_started (dbus.rs)

## Question
Can an unprivileged attacker modify or influence a field that `signup_started` in [src/dbus.rs](src/dbus.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/dbus.rs](src/dbus.rs) -> `signup_started` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `signup_started`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `signup_started` covers the full transmitted structure.
