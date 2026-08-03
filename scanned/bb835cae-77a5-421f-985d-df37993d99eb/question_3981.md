# Q3981: touch can break reserve or fee invariants

## Question
Can an unprivileged attacker call `touch` with adversarial amounts, fees, or prices and make the pallet compute inconsistent reserve, fee, share, or debt values across `Pools`, `LP issuance`, and `pool reserves`?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::touch
- Entrypoint: signed extrinsic `touch`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Push precision loss, stale price assumptions, or ordering-sensitive updates so economic state diverges across the pool or market ledger.
- Invariant to test: Reserve balances, fee accounting, and issued claims must stay mutually consistent before and after the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Fuzz exact-output/exact-input, tiny-amount, large-amount, and repeated-swap paths and assert reserve and issuance conservation.
