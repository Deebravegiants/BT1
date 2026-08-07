# Q2965: get_not_unique_leader_tpus can be driven into unbounded work (cluster_tpu_info.rs)

## Question
Can an unprivileged attacker entering through one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2 reach `get_not_unique_leader_tpus` in `rpc/src/cluster_tpu_info.rs` with a key that exists on an ancestor fork but not the current one, and make `get_not_unique_leader_tpus` iterate over an attacker-sized set far past the per-slot budget, so that the invariant "Iteration count in `get_not_unique_leader_tpus` is bounded by a constant or by a value the transaction pays for." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `rpc/src/cluster_tpu_info.rs` -> `get_not_unique_leader_tpus()` (around line 121)
- Entrypoint: one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2
- Attacker controls: a key that exists on an ancestor fork but not the current one
- Exploit idea: Grow the attacker-controlled collection `get_not_unique_leader_tpus` iterates so a single transaction pins the replay thread far past the slot budget.
- Invariant to test: Iteration count in `get_not_unique_leader_tpus` is bounded by a constant or by a value the transaction pays for.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Benchmark `get_not_unique_leader_tpus` as the attacker-controlled size grows; assert runtime stays under the per-slot budget.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
