# Q0043: parse_field parse failure leaves partial state applied (network/mecard.rs)

## Question
Can an unprivileged attacker present a QR that fails validation *after* `parse_field` in [src/network/mecard.rs](src/network/mecard.rs) has already applied part of it (identity, mode, network, or policy), leaving the Orb running with half-applied attacker-controlled state?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse_field` (function)
- Entrypoint: Malformed QR presented during the scan phase
- Attacker controls: which field of the payload is made invalid, and its position
- Exploit idea: Place the invalid field last so earlier fields are committed before the error path is taken.
- Invariant to test: Parsing is atomic: no attacker-derived value is committed to session state unless the whole payload validates.
- Expected Immunefi impact: Attacker-controlled state persisted into a signup that should have been rejected
- Fast validation: Integration test: submit a payload invalid only in its final field, then assert no session/network/policy mutation occurred.
