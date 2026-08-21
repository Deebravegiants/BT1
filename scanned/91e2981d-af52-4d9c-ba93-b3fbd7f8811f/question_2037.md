# Q2037: Field-name/case confusion in download (config.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `download` in [src/config.rs](src/config.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/config.rs](src/config.rs) -> `download` (function)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `download` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `download` with mis-cased fields asserting an explicit error.
