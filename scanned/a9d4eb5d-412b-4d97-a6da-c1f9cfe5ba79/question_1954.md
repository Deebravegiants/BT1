# Q1954: Deserialization of untyped/permissive schema in from_str (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker exploit permissive deserialization in `from_str` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) (unknown fields ignored, untagged enums, string-to-number coercion) so an ambiguous document is interpreted one way here and another way where it is validated?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from_str` (function)
- Entrypoint: Documents whose fields they influenced in the same session
- Attacker controls: field naming, duplication, and type shape of the document
- Exploit idea: Check `from_str` for `deny_unknown_fields` and unambiguous enum tagging.
- Invariant to test: Deserialization is strict and unambiguous; unknown or duplicated fields are errors.
- Expected Immunefi impact: Security-relevant configuration parsed differently than validated
- Fast validation: Differential test parsing duplicate/unknown-field documents through `from_str`.
