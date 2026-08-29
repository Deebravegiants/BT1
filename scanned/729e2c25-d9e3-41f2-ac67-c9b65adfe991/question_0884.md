# Q0884: calc-liq-debt-repay via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `calc-liq-debt-repay` (mainnet/contracts/market/v0-4-market.clar:723) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it takes the liquidation factor times the debt with `mul-bps-down`, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:723` -> `calc-liq-debt-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `calc-liq-debt-repay` takes the liquidation factor times the debt with `mul-bps-down`. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `calc-liq-debt-repay` returns is identical in both runs; a divergence confirms the finding.
