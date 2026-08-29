# Q1759: insert via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
`insert` (mainnet/contracts/market/v0-market-vault.clar:159) rewrites the whole registry entry for a user id. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing `receiver`, including a contract principal, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with `receiver`, including a contract principal, then read `insert` state before and after in the same block and assert the two sides of the invariant are equal.
