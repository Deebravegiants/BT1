# Q0607: create_pool replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `create_pool` in the same or adjacent blocks and make settlement happen twice before `pool reserves` closes the first path?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::create_pool
- Entrypoint: signed extrinsic `create_pool`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
