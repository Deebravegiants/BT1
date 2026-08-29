# Q5659: mask-to-list-iter via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
`mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the set of assets held, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with the set of assets held, then read `mask-to-list-iter` state before and after in the same block and assert the two sides of the invariant are equal.
