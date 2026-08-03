# Q0685: create_with_pool_id replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `create_with_pool_id` in the same or adjacent blocks and make settlement happen twice before `RewardPools` closes the first path?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::create_with_pool_id
- Entrypoint: signed extrinsic `create_with_pool_id`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
