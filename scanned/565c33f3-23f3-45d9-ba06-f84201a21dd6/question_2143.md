# Q2143: poke_deposit can pay twice from the same completed object

## Question
Can an unprivileged attacker use `poke_deposit` and a public follow-up to claim, refund, or reclaim value twice from the same spend, bounty, tip, or referendum object?

## Target
- File/function: substrate/frame/bounties/src/lib.rs::poke_deposit
- Entrypoint: signed extrinsic `poke_deposit`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Search for terminal-state writes that happen in one storage item but not another public payout gate.
- Invariant to test: A completed governance object must have no second public path that still pays or refunds value.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Drive the object to completion and then call every public payout, refund, reclaim, and status function that can still reference it.
