# Q0755: Signature covers less than the security-relevant data in handle_save_fusion_rn_fi (agents/image_notary.rs)

## Question
Can an unprivileged attacker modify or influence a field that `handle_save_fusion_rn_fi` in [src/agents/image_notary.rs](src/agents/image_notary.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_save_fusion_rn_fi` (function)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `handle_save_fusion_rn_fi`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `handle_save_fusion_rn_fi` covers the full transmitted structure.
