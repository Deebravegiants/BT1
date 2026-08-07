# Q3012: get_leader_tpus charges far less than it costs (tpu_info.rs)

## Question
Can an unprivileged attacker entering through one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2 reach `get_leader_tpus` in `send-transaction-service/src/tpu_info.rs` with an index range the attacker can grow without bound, and make the real CPU/memory cost of `get_leader_tpus` exceed the units charged for it, so that the invariant "Charged cost is a monotone upper bound on real cost for every input shape." breaks and the result is DoS?

## Target
- File/function: `send-transaction-service/src/tpu_info.rs` -> `get_leader_tpus()` (around line 15)
- Entrypoint: one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2
- Attacker controls: an index range the attacker can grow without bound
- Exploit idea: Find the input shape where `get_leader_tpus`'s real CPU/memory/IO cost grows much faster than the compute units or fee charged for it.
- Invariant to test: Charged cost is a monotone upper bound on real cost for every input shape.
- Expected Immunefi impact: DoS - remote resource exhaustion via non-RPC protocols (315-1,250 SOL)
- Fast validation: Measure real time/allocations versus units charged across input sizes; assert cost/CU ratio stays bounded.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
High. An unprivileged attacker can make compute-budget, cost-model, or fee accounting charge materially less than the real CPU, memory, or account-load work performed, exhausting block capacity or node resources below true cost.
