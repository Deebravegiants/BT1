# Q0716: withdraw_unbonded replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `withdraw_unbonded` in the same or adjacent blocks and make settlement happen twice before `Validators` closes the first path?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::withdraw_unbonded
- Entrypoint: signed extrinsic `withdraw_unbonded`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
