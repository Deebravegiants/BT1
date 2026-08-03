# Q0666: purchase_credit replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `purchase_credit` in the same or adjacent blocks and make settlement happen twice before `InstaPoolContribution` closes the first path?

## Target
- File/function: substrate/frame/broker/src/lib.rs::purchase_credit
- Entrypoint: signed extrinsic `purchase_credit`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
