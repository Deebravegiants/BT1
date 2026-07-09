# Q611: votes remove_votes_for_proposal stale or outsider voting

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/contract/src/primitives/votes.rs::remove_votes_for_proposal` so that stale or outsider voting power moves protocol state, breaking the invariant that only the current authorized participant set may create or preserve governance power, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/primitives/votes.rs:96::remove_votes_for_proposal
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: stale or outsider voting power moves protocol state
- Invariant to test: only the current authorized participant set may create or preserve governance power
- Expected Immunefi impact: Contract execution flows
- Fast validation: call across participant-churn boundaries and verify whether removed or never-authorized accounts can still influence thresholds or final execution
