# Q1941: Identifier construction in SaveIdentificationImagesInput allows collision (agents/image_notary.rs)

## Question
Can an unprivileged attacker construct inputs that make `SaveIdentificationImagesInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveIdentificationImagesInput` (type)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `SaveIdentificationImagesInput` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `SaveIdentificationImagesInput` asserting injectivity across component tuples.
