# Q3042: get_program_kind grows memory without an enforced bound (builtin_programs_filter.rs)

## Question
Can an unprivileged attacker entering through a transaction broadcast to a public TPU/QUIC endpoint by an ordinary funded keypair reach `get_program_kind` in `compute-budget-instruction/src/builtin_programs_filter.rs` with a missing entry that makes the loader fall back to a default instead of failing, and grow the buffer `get_program_kind` feeds without any eviction bound taking effect, so that the invariant "Every container this path writes into has an enforced capacity or eviction policy." breaks and the result is DoS?

## Target
- File/function: `compute-budget-instruction/src/builtin_programs_filter.rs` -> `get_program_kind()` (around line 37)
- Entrypoint: a transaction broadcast to a public TPU/QUIC endpoint by an ordinary funded keypair
- Attacker controls: a missing entry that makes the loader fall back to a default instead of failing
- Exploit idea: Repeatedly drive `get_program_kind` so a buffer, map, or cache it feeds grows without eviction, exhausting node memory below the cost the attacker pays.
- Invariant to test: Every container this path writes into has an enforced capacity or eviction policy.
- Expected Immunefi impact: DoS - remote resource exhaustion via non-RPC protocols (315-1,250 SOL)
- Fast validation: Stress the path and assert the container's size plateaus rather than growing linearly with attacker input.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
High. An unprivileged attacker can make compute-budget, cost-model, or fee accounting charge materially less than the real CPU, memory, or account-load work performed, exhausting block capacity or node resources below true cost.
