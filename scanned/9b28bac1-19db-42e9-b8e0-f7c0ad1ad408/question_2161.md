# Q2161: retract_tip can pay twice from the same completed object

## Question
Can an unprivileged attacker use `retract_tip` and a public follow-up to claim, refund, or reclaim value twice from the same spend, bounty, tip, or referendum object?

## Target
- File/function: substrate/frame/tips/src/lib.rs::retract_tip
- Entrypoint: signed extrinsic `retract_tip`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Search for terminal-state writes that happen in one storage item but not another public payout gate.
- Invariant to test: A completed governance object must have no second public path that still pays or refunds value.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Drive the object to completion and then call every public payout, refund, reclaim, and status function that can still reference it.
