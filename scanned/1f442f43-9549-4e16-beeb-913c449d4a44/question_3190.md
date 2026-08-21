# Q3190: Response field consumed by request_tiered_package without validation (backend/presigned_url.rs)

## Question
Can an unprivileged attacker exploit `request_tiered_package` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) consuming a response field they influenced earlier in the same session (echoed identity, region, URL, policy) without re-validating it, so their earlier input steers a later security decision?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `request_tiered_package` (function)
- Entrypoint: Their own session, where earlier-supplied values are echoed back
- Attacker controls: the value they injected earlier that is later echoed
- Exploit idea: Identify which fields `request_tiered_package` trusts and whether any trace back to session input.
- Invariant to test: Values echoed from earlier session input are re-validated before use in a security decision.
- Expected Immunefi impact: Attacker input laundered through a round-trip into a trusted decision
- Fast validation: Integration test echoing an attacker-shaped field and asserting re-validation.
