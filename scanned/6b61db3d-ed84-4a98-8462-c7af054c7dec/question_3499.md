# Q3499: subset via collateral-add: count one deposit as backing for two simultaneous claims

## Question
`subset` (mainnet/contracts/market/v0-market-vault.clar:100) tests bitmask containment. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the position's existing collateral and debt composition, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the position's existing collateral and debt composition, then read `subset` state before and after in the same block and assert the two sides of the invariant are equal.
