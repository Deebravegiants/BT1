# Q0404: find-asset via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `find-asset` returns is identical in both runs; a divergence confirms the finding.
