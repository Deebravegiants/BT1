# Q2488: precursor and follow-up calls around pool_withdraw_unbonded can exploit intermediate sta

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `pool_withdraw_unbonded`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::pool_withdraw_unbonded
- Entrypoint: signed extrinsic `pool_withdraw_unbonded`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
