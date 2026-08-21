# Q1997: Field-name/case confusion in BackendKey (backend/user_status.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `BackendKey` in [src/backend/user_status.rs](src/backend/user_status.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/backend/user_status.rs](src/backend/user_status.rs) -> `BackendKey` (type)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `BackendKey` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `BackendKey` with mis-cased fields asserting an explicit error.
