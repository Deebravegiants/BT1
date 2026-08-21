# Q1942: Identifier construction in SaveIrNetEstimateInput allows collision (agents/image_notary.rs)

## Question
Can an unprivileged attacker construct inputs that make `SaveIrNetEstimateInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveIrNetEstimateInput` (type)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `SaveIrNetEstimateInput` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `SaveIrNetEstimateInput` asserting injectivity across component tuples.
