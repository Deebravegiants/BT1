# Q3883: resolve-ststx via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
`resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with `amount`, then read `resolve-ststx` state before and after in the same block and assert the two sides of the invariant are equal.
