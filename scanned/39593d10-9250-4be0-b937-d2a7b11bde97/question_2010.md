# Q2010: Field-name/case confusion in Wifi (backend/status.rs)

## Question
Can an unprivileged attacker exploit case or alias mismatches in `Wifi` in [src/backend/status.rs](src/backend/status.rs) (PascalCase vs snake_case, aliased fields) so a security-relevant field silently falls back to its default because the expected name never matched?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `Wifi` (type)
- Entrypoint: Documents whose field naming they influence
- Attacker controls: field-name casing and aliasing
- Exploit idea: Check `Wifi` for a rename policy and whether missing fields default rather than error.
- Invariant to test: Missing security-relevant fields are errors, not defaults.
- Expected Immunefi impact: Security controls silently defaulted off by a naming mismatch
- Fast validation: Unit-test `Wifi` with mis-cased fields asserting an explicit error.
