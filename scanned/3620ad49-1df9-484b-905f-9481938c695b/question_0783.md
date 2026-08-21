# Q0783: Identifier construction in new allows collision (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker construct inputs that make `new` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `new` (function)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `new` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `new` asserting injectivity across component tuples.
