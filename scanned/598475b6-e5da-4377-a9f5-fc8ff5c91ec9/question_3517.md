# Q3517: Deserialization in try_parse trusts length/shape fields (qr_scan/mod.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `try_parse` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `try_parse` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `try_parse` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `try_parse` with mismatched shape headers asserting graceful rejection.
