# Q2382: Deserialization in parse trusts length/shape fields (network/mecard.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `parse` in [src/network/mecard.rs](src/network/mecard.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `parse` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `parse` with mismatched shape headers asserting graceful rejection.
