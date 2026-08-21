# Q2200: Deserialization in serialize trusts length/shape fields (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `serialize` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `serialize` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `serialize` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `serialize` with mismatched shape headers asserting graceful rejection.
