# Q3623: recalculate_stake_rewards rounding drift is attacker-directed (calculation.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `recalculate_stake_rewards` in `runtime/src/bank/partitioned_epoch_rewards/calculation.rs` with values chosen so the arithmetic saturates, wraps, or rounds toward the attacker, and make every rounding step inside `recalculate_stake_rewards` land in the attacker's favour across repeated calls, so that the invariant "Rounding is either exact or always rounds against the caller, and repeated operations cannot accumulate a positive drift." breaks and the result is Loss of Funds?

## Target
- File/function: `runtime/src/bank/partitioned_epoch_rewards/calculation.rs` -> `recalculate_stake_rewards()` (around line 1038)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: values chosen so the arithmetic saturates, wraps, or rounds toward the attacker
- Exploit idea: Choose amounts so every rounding step in `recalculate_stake_rewards` lands in the attacker's favour, then repeat the flow to accumulate the drift into a withdrawable balance.
- Invariant to test: Rounding is either exact or always rounds against the caller, and repeated operations cannot accumulate a positive drift.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Loop the operation N times in a unit test with adversarial amounts and assert the attacker's net balance never increases.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
