# Q2023: Deserialization of untyped/permissive schema in UrlType (backend/presigned_url.rs)

## Question
Can an unprivileged attacker exploit permissive deserialization in `UrlType` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) (unknown fields ignored, untagged enums, string-to-number coercion) so an ambiguous document is interpreted one way here and another way where it is validated?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `UrlType` (type)
- Entrypoint: Documents whose fields they influenced in the same session
- Attacker controls: field naming, duplication, and type shape of the document
- Exploit idea: Check `UrlType` for `deny_unknown_fields` and unambiguous enum tagging.
- Invariant to test: Deserialization is strict and unambiguous; unknown or duplicated fields are errors.
- Expected Immunefi impact: Security-relevant configuration parsed differently than validated
- Fast validation: Differential test parsing duplicate/unknown-field documents through `UrlType`.
