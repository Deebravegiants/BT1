# Q1180: key event vote_abort historic approvals silently authorize

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/contract/src/state/key_event.rs::vote_abort` so that historic approvals silently authorize a fresh state transition, breaking the invariant that proposal identity, epoch, and participant set must all be part of governance authorization, and leading to Unauthorized transaction?

## Target
- File/function: crates/contract/src/state/key_event.rs:145::vote_abort
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: historic approvals silently authorize a fresh state transition
- Invariant to test: proposal identity, epoch, and participant set must all be part of governance authorization
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: create one proposal, mutate the surrounding state, then submit a second proposal that partially overlaps and check whether previous approvals still count
