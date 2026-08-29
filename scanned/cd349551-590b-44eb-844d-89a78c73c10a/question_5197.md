# Q5197: insert via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the order of accrual versus price resolution inside the let, drive `insert` (mainnet/contracts/market/v0-market-vault.clar:159) — which rewrites the whole registry entry for a user id — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the order of accrual versus price resolution inside the let, then read `insert` state before and after in the same block and assert the two sides of the invariant are equal.
