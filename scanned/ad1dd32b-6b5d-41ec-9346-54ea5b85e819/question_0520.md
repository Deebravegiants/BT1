# Q520: dkg verify_proof_of_knowledge old stored bytes silently

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/threshold-signatures/src/dkg.rs::verify_proof_of_knowledge` so that old stored bytes silently change meaning in security-sensitive state, breaking the invariant that durable serialized state must remain backward-compatible without changing the authorization meaning of existing bytes, and leading to Contract execution flows?

## Target
- File/function: crates/threshold-signatures/src/dkg.rs:174::verify_proof_of_knowledge
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: old stored bytes silently change meaning in security-sensitive state
- Invariant to test: durable serialized state must remain backward-compatible without changing the authorization meaning of existing bytes
- Expected Immunefi impact: Contract execution flows
- Fast validation: persist crafted state bytes through one representation, reload through the next conversion path, and diff the resulting runtime security state
