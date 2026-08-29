# Q1639: add-user-collateral via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
`add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) adds to the collateral row with a graceful u0 default. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing `receiver`, including a contract principal, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with `receiver`, including a contract principal, then read `add-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
