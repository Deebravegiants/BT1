# Q3036: Identifier construction in make_face_tar allows collision (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker construct inputs that make `make_face_tar` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_tar` (function)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `make_face_tar` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `make_face_tar` asserting injectivity across component tuples.
