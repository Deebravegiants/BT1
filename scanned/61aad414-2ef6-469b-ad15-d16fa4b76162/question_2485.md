# Q2485: precursor and follow-up calls around create_with_pool_id can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `create_with_pool_id`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::create_with_pool_id
- Entrypoint: signed extrinsic `create_with_pool_id`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
