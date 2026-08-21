# Q3160: Field-name/case confusion in empty_string_is_none (backend/signup_poll.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `empty_string_is_none` in [src/backend/signup_poll.rs](src/backend/signup_poll.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/backend/signup_poll.rs](src/backend/signup_poll.rs) -> `empty_string_is_none` (function)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `empty_string_is_none` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `empty_string_is_none` with mis-cased fields asserting an explicit error.
