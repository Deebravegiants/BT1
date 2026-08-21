# Q0027: Deserialization in decode_rxing trusts length/shape fields (agents/qr_code.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `decode_rxing` in [src/agents/qr_code.rs](src/agents/qr_code.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/agents/qr_code.rs](src/agents/qr_code.rs) -> `decode_rxing` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `decode_rxing` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `decode_rxing` with mismatched shape headers asserting graceful rejection.
