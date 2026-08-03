# Q2600: precursor and follow-up calls around propose can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `propose`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/democracy/src/lib.rs::propose
- Entrypoint: signed extrinsic `propose`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
