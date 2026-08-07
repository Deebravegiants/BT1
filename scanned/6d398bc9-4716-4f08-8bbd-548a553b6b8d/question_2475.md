# Q2475: is_one charges far less than it costs (lib.rs)

## Question
Can an unprivileged attacker entering through raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port reach `is_one` in `unified-scheduler-logic/src/lib.rs` with a maximal instruction/account count that pushes the path to its declared limit, and make the real CPU/memory cost of `is_one` exceed the units charged for it, so that the invariant "Charged cost is a monotone upper bound on real cost for every input shape." breaks and the result is DoS?

## Target
- File/function: `unified-scheduler-logic/src/lib.rs` -> `is_one()` (around line 171)
- Entrypoint: raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port
- Attacker controls: a maximal instruction/account count that pushes the path to its declared limit
- Exploit idea: Find the input shape where `is_one`'s real CPU/memory/IO cost grows much faster than the compute units or fee charged for it.
- Invariant to test: Charged cost is a monotone upper bound on real cost for every input shape.
- Expected Immunefi impact: DoS - remote resource exhaustion via non-RPC protocols (315-1,250 SOL)
- Fast validation: Measure real time/allocations versus units charged across input sizes; assert cost/CU ratio stays bounded.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
High. An unprivileged attacker can make compute-budget, cost-model, or fee accounting charge materially less than the real CPU, memory, or account-load work performed, exhausting block capacity or node resources below true cost.
