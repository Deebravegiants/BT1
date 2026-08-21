# Q3569: check_hex_string_format parse failure leaves partial state applied (wpa-supplicant-interface/join.rs)

## Question
Can an unprivileged attacker present a QR that fails validation *after* `check_hex_string_format` in [wpa-supplicant-interface/src/join.rs](wpa-supplicant-interface/src/join.rs) has already applied part of it (identity, mode, network, or policy), leaving the Orb running with half-applied attacker-controlled state?

## Target
- File/function: [wpa-supplicant-interface/src/join.rs](wpa-supplicant-interface/src/join.rs) -> `check_hex_string_format` (function)
- Entrypoint: Malformed QR presented during the scan phase
- Attacker controls: which field of the payload is made invalid, and its position
- Exploit idea: Place the invalid field last so earlier fields are committed before the error path is taken.
- Invariant to test: Parsing is atomic: no attacker-derived value is committed to session state unless the whole payload validates.
- Expected Immunefi impact: Attacker-controlled state persisted into a signup that should have been rejected
- Fast validation: Integration test: submit a payload invalid only in its final field, then assert no session/network/policy mutation occurred.
