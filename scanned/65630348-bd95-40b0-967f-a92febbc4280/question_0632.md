# Q0632: set_reserves replay can double-apply settlement

## Question
Can an unprivileged attacker repeat `set_reserves` in the same or adjacent blocks and make settlement happen twice before `Approvals` closes the first path?

## Target
- File/function: substrate/frame/assets/src/lib.rs::set_reserves
- Entrypoint: signed extrinsic `set_reserves`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for stale markers, insufficient idempotency checks, or secondary paths that do not bind tightly enough to prior execution.
- Invariant to test: The same economic action must not be claimable, withdrawable, refundable, or spendable twice.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay the exact call and a minimally changed variant; assert no second payout or second state transition occurs.
