# Q1975: next_completed_index grows memory without an enforced bound (blockstore_meta.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `next_completed_index` in `ledger/src/blockstore_meta.rs` with an index range the attacker can grow without bound, and grow the buffer `next_completed_index` feeds without any eviction bound taking effect, so that the invariant "Every container this path writes into has an enforced capacity or eviction policy." breaks and the result is DoS?

## Target
- File/function: `ledger/src/blockstore_meta.rs` -> `next_completed_index()` (around line 108)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: an index range the attacker can grow without bound
- Exploit idea: Repeatedly drive `next_completed_index` so a buffer, map, or cache it feeds grows without eviction, exhausting node memory below the cost the attacker pays.
- Invariant to test: Every container this path writes into has an enforced capacity or eviction policy.
- Expected Immunefi impact: DoS - remote resource exhaustion via non-RPC protocols (315-1,250 SOL)
- Fast validation: Stress the path and assert the container's size plateaus rather than growing linearly with attacker input.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
High. An unprivileged attacker can make compute-budget, cost-model, or fee accounting charge materially less than the real CPU, memory, or account-load work performed, exhausting block capacity or node resources below true cost.
