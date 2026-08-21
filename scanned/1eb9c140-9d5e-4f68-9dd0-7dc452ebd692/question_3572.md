# Q3572: Deserialization in parse_output trusts length/shape fields (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `parse_output` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `parse_output` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `parse_output` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `parse_output` with mismatched shape headers asserting graceful rejection.
