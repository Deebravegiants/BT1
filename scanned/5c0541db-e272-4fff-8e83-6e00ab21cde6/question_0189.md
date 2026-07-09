# Q189: tee state lookup_node_id_by_signer_pk a non-approved runtime lands

## Question
Can an unprivileged NEAR account or outsider node trying to look like a valid participant enter through `submit_participant_info / verify_tee` and use attestation bytes, node identity fields, responder/signer keys, repeated submissions, and timing around cleanup or re-verification to drive the code path through `crates/contract/src/tee/tee_state.rs::lookup_node_id_by_signer_pk` so that a non-approved runtime lands inside an approved bucket, breaking the invariant that allowed runtime measurements must be compared canonically and consistently across proposal, storage, and verification, and leading to Unauthorized transaction?

## Target
- File/function: crates/contract/src/tee/tee_state.rs:454::lookup_node_id_by_signer_pk
- Entrypoint: `submit_participant_info / verify_tee`
- Attacker controls: attestation bytes, node identity fields, responder/signer keys, repeated submissions, and timing around cleanup or re-verification
- Exploit idea: a non-approved runtime lands inside an approved bucket
- Invariant to test: allowed runtime measurements must be compared canonically and consistently across proposal, storage, and verification
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: submit semantically equivalent-but-differently-encoded measurement material and diff proposal acceptance against runtime verification results
