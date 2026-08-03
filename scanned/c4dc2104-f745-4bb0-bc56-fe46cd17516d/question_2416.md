# Q2416: precursor and follow-up calls around create_pool can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `create_pool`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::create_pool
- Entrypoint: signed extrinsic `create_pool`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
