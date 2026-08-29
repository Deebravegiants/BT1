# Q0284: calc-liq-factor-bound via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `calc-liq-factor-bound` (mainnet/contracts/market/v0-4-market.clar:718) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it scales the penalty between a min and a max, capped at the max, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:718` -> `calc-liq-factor-bound`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `calc-liq-factor-bound` returns is identical in both runs; a divergence confirms the finding.
