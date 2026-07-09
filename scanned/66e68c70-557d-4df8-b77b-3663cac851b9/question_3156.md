# Q3156: handshake p2p_handshake_listener old authenticated traffic contaminates

## Question
Can a below-threshold Byzantine participant node enter through `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction` and use authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state to drive the code path through `crates/node/src/network/handshake.rs::p2p_handshake_listener` so that old authenticated traffic contaminates a new protocol run, breaking the invariant that a connection version change must invalidate every stale frame and stale sender state tied to the old connection, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/node/src/network/handshake.rs:134::p2p_handshake_listener
- Entrypoint: `authenticated P2P message flow during sign / request_app_private_key / verify_foreign_transaction`
- Attacker controls: authenticated MPC/P2P frames, connection churn, message ordering, duplicates, channel/task identifiers, and stale session state
- Exploit idea: old authenticated traffic contaminates a new protocol run
- Invariant to test: a connection version change must invalidate every stale frame and stale sender state tied to the old connection
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: disconnect and reconnect a Byzantine participant mid-protocol, then replay old frames and check whether the new session accepts them
