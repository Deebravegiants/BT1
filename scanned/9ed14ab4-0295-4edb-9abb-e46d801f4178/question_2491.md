# Q2491: find-and-resolve-asset-value via liquidate: destroy value through a truncation the opposite operation 

## Question
`find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `min-collateral-expected`, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `min-collateral-expected`, then read `find-and-resolve-asset-value` state before and after in the same block and assert the two sides of the invariant are equal.
