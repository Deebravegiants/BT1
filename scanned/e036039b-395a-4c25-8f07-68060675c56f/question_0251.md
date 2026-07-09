# Q251: cleanup delete_stale_triples_and_presignatures cross-task message confusion feeds

## Question
Can a below-threshold Byzantine participant node enter through `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction` and use authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state to drive the code path through `crates/node/src/assets/cleanup.rs::delete_stale_triples_and_presignatures` so that cross-task message confusion feeds attacker-chosen protocol state into the wrong computation, breaking the invariant that channel_id, task_id, participant set, and connection epoch must uniquely identify one live computation, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/assets/cleanup.rs:21::delete_stale_triples_and_presignatures
- Entrypoint: `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction`
- Attacker controls: authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state
- Exploit idea: cross-task message confusion feeds attacker-chosen protocol state into the wrong computation
- Invariant to test: channel_id, task_id, participant set, and connection epoch must uniquely identify one live computation
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: run two overlapping tasks, replay frames across them, and inspect whether a receiver accepts bytes from the wrong channel or task
