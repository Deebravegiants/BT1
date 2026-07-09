# Q1424: temporary start_generating_keyshare authenticated traffic is attributed

## Question
Can a below-threshold Byzantine participant node enter through `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction` and use authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state to drive the code path through `crates/node/src/keyshare/temporary.rs::start_generating_keyshare` so that authenticated traffic is attributed to the wrong participant id, breaking the invariant that every accepted message must be bound end-to-end to one authenticated participant identity, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/keyshare/temporary.rs:51::start_generating_keyshare
- Entrypoint: `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction`
- Attacker controls: authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state
- Exploit idea: authenticated traffic is attributed to the wrong participant id
- Invariant to test: every accepted message must be bound end-to-end to one authenticated participant identity
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: exercise reconnects or stale manager state and verify whether an authenticated peer can cause messages to be recorded under a different participant id
