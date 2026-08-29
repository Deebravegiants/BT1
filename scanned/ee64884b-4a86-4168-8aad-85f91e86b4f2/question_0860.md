# Q0860: iter-find-superset via collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it short-circuits on the first superset match, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `iter-find-superset` returns is identical in both runs; a divergence confirms the finding.
