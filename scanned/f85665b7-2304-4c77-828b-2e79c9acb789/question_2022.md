# Q2022: Field-name/case confusion in Response (backend/presigned_url.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `Response` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `Response` (type)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `Response` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `Response` with mis-cased fields asserting an explicit error.
