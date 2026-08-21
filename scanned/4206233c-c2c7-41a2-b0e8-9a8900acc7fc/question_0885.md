# Q0885: Deserialization in drop_oldest trusts length/shape fields (agents/data_uploader.rs)

## Question
Can an unprivileged attacker supply a serialized artifact whose declared length/shape does not match its content, so `drop_oldest` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) allocates or indexes on the declared value and panics or over-allocates?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `drop_oldest` (function)
- Entrypoint: Artifacts whose content originates in attacker-controlled capture/scan data
- Attacker controls: declared shape/length fields versus actual payload bytes
- Exploit idea: Check `drop_oldest` for cross-validation of declared dimensions against actual byte length.
- Invariant to test: Declared dimensions are validated against actual data before allocation or indexing.
- Expected Immunefi impact: Crash or memory exhaustion in the signup data path
- Fast validation: Fuzz `drop_oldest` with mismatched shape headers asserting graceful rejection.
