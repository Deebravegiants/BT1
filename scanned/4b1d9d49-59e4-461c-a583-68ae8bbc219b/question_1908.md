# Q1908: Identifier construction in TokenError allows collision (identification.rs)

## Question
Can an unprivileged attacker construct inputs that make `TokenError` in [src/identification.rs](src/identification.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `TokenError` (type)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `TokenError` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `TokenError` asserting injectivity across component tuples.
