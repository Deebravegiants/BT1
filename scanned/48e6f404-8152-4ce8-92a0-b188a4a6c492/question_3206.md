# Q3206: Field-name/case confusion in store (config.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `store` in [src/config.rs](src/config.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/config.rs](src/config.rs) -> `store` (function)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `store` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `store` with mis-cased fields asserting an explicit error.
