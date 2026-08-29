# Q3019: find via liquidate: count one deposit as backing for two simultaneous claims

## Question
`find` (mainnet/contracts/registry/v0-assets.clar:135) resolves an asset record from a principal through the `reverse` map. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `collateral-receiver`, then read `find` state before and after in the same block and assert the two sides of the invariant are equal.
