# Q2471: precursor and follow-up calls around purchase_credit can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `purchase_credit`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/broker/src/lib.rs::purchase_credit
- Entrypoint: signed extrinsic `purchase_credit`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
