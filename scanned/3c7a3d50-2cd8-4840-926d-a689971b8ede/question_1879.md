# Q1879: write-feed via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
`write-feed` (mainnet/contracts/market/v0-4-market.clar:129) applies one Pyth price-feed update and folds its status. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing `receiver`, including a contract principal, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with `receiver`, including a contract principal, then read `write-feed` state before and after in the same block and assert the two sides of the invariant are equal.
