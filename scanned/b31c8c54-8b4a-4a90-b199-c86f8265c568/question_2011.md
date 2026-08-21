# Q2011: Deserialization of untyped/permissive schema in WifiQuality (backend/status.rs)

## Question
Can an unprivileged attacker exploit permissive deserialization in `WifiQuality` in [src/backend/status.rs](src/backend/status.rs) (unknown fields ignored, untagged enums, string-to-number coercion) so an ambiguous document is interpreted one way here and another way where it is validated?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `WifiQuality` (type)
- Entrypoint: Documents whose fields they influenced in the same session
- Attacker controls: field naming, duplication, and type shape of the document
- Exploit idea: Check `WifiQuality` for `deny_unknown_fields` and unambiguous enum tagging.
- Invariant to test: Deserialization is strict and unambiguous; unknown or duplicated fields are errors.
- Expected Immunefi impact: Security-relevant configuration parsed differently than validated
- Fast validation: Differential test parsing duplicate/unknown-field documents through `WifiQuality`.
