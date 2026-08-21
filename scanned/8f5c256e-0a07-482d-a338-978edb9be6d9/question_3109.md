# Q3109: Field-name/case confusion in decrypt_and_unseal (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `decrypt_and_unseal` in [src/agents/image_notary.rs](src/agents/image_notary.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `decrypt_and_unseal` (function)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `decrypt_and_unseal` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `decrypt_and_unseal` with mis-cased fields asserting an explicit error.
