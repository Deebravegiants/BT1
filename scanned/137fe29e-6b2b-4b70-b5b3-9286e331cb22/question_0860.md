# Q0860: Field-name/case confusion in load_or_default (config.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `load_or_default` in [src/config.rs](src/config.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/config.rs](src/config.rs) -> `load_or_default` (function)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `load_or_default` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `load_or_default` with mis-cased fields asserting an explicit error.
