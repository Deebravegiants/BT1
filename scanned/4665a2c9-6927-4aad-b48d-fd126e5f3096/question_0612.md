# Q0612: deposit_reward_tokens replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `deposit_reward_tokens` in the same or adjacent blocks and make settlement happen twice before `reward_per_token` closes the first path?

## Target
- File/function: substrate/frame/asset-rewards/src/lib.rs::deposit_reward_tokens
- Entrypoint: signed extrinsic `deposit_reward_tokens`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
