# Q1224: running vote_add_domains execution uses stale preconditions

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/contract/src/state/running.rs::vote_add_domains` so that execution uses stale preconditions, breaking the invariant that a proposal must be revalidated against current state at the moment it takes effect, and leading to Unauthorized transaction?

## Target
- File/function: crates/contract/src/state/running.rs:214::vote_add_domains
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: execution uses stale preconditions
- Invariant to test: a proposal must be revalidated against current state at the moment it takes effect
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: prepare a proposal, invalidate its assumptions through another public action, then finalize the original proposal and inspect whether execution still proceeds
