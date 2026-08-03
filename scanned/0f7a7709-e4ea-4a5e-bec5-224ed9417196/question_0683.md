# Q0683: claim_payout_other replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `claim_payout_other` in the same or adjacent blocks and make settlement happen twice before `RewardPools` closes the first path?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::claim_payout_other
- Entrypoint: signed extrinsic `claim_payout_other`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
