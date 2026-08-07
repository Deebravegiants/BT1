# Q3448: calculate_non_circulating_supply breaks lamport conservation (non_circulating_supply.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `calculate_non_circulating_supply` in `runtime/src/non_circulating_supply.rs` with amounts split across many transactions so per-step rounding accumulates, and make the lamports `calculate_non_circulating_supply` removes differ from the lamports it credits, so that the invariant "Sum of lamports before and after the operation is equal, except for the explicit fee/rent burn." breaks and the result is Loss of Funds?

## Target
- File/function: `runtime/src/non_circulating_supply.rs` -> `calculate_non_circulating_supply()` (around line 19)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: amounts split across many transactions so per-step rounding accumulates
- Exploit idea: Drive `calculate_non_circulating_supply` so the lamports it removes and the lamports it adds differ, minting or destroying value outside the inflation schedule.
- Invariant to test: Sum of lamports before and after the operation is equal, except for the explicit fee/rent burn.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Property test around `calculate_non_circulating_supply`: assert `sum_lamports_before == sum_lamports_after + burned` over randomized inputs.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
