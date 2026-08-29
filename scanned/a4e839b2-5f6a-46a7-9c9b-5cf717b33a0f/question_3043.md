# Q3043: create via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
`create` (mainnet/contracts/market/v0-market-vault.clar:150) binds a principal to a fresh numeric id. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with `amount`, then read `create` state before and after in the same block and assert the two sides of the invariant are equal.
