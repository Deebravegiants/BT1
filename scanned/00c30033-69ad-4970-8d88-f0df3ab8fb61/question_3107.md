# Q3107: Deserialization of untyped/permissive schema in is_enough_space (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit permissive deserialization in `is_enough_space` in [src/agents/image_notary.rs](src/agents/image_notary.rs) (unknown fields ignored, untagged enums, string-to-number coercion) so an ambiguous document is interpreted one way here and another way where it is validated?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `is_enough_space` (function)
- Entrypoint: Documents whose fields they influenced in the same session
- Attacker controls: field naming, duplication, and type shape of the document
- Exploit idea: Check `is_enough_space` for `deny_unknown_fields` and unambiguous enum tagging.
- Invariant to test: Deserialization is strict and unambiguous; unknown or duplicated fields are errors.
- Expected Immunefi impact: Security-relevant configuration parsed differently than validated
- Fast validation: Differential test parsing duplicate/unknown-field documents through `is_enough_space`.
