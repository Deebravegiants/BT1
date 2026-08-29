# Q3091: interpolate-rate via collateral-add: count one deposit as backing for two simultaneous claims

## Question
`interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) interpolates between packed u16 curve points. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the position's existing collateral and debt composition, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the position's existing collateral and debt composition, then read `interpolate-rate` state before and after in the same block and assert the two sides of the invariant are equal.
