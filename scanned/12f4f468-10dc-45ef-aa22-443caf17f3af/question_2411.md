# Q2411: from_sharable_pubkeys is not deterministic across nodes (pubkeys_ptr.rs)

## Question
Can an unprivileged attacker entering through raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port reach `from_sharable_pubkeys` in `scheduling-utils/src/pubkeys_ptr.rs` with an empty or single-element set at the boundary of the accumulation, and make the account locks held by the scheduler disagree with the accounts the executing batch actually touches, so that the invariant "For identical committed state and feature set, `from_sharable_pubkeys` returns byte-identical results on every node." breaks and the result is Consensus/Safety Violation?

## Target
- File/function: `scheduling-utils/src/pubkeys_ptr.rs` -> `from_sharable_pubkeys()` (around line 36)
- Entrypoint: raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port
- Attacker controls: an empty or single-element set at the boundary of the accumulation
- Exploit idea: Find input to `from_sharable_pubkeys` whose result depends on iteration order, map ordering, cache warmth, timing, or float/HashMap behaviour rather than only on committed state.
- Invariant to test: For identical committed state and feature set, `from_sharable_pubkeys` returns byte-identical results on every node.
- Expected Immunefi impact: Consensus/Safety Violation - honest nodes commit different state, bank-hash mismatch or fork (3,125-12,500 SOL)
- Fast validation: Differential test: run `from_sharable_pubkeys` twice with shuffled input ordering and a cold vs warm cache; assert identical output.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can submit a transaction whose loading, sanitization, ALT resolution, or execution result differs between honest validators, causing bank-hash divergence, a fork, or an unbootable ledger replay.
