# Q4208: calc-liquidation-params via liquidate-multi: mint shares whose backing was never received

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `calc-liquidation-params` (mainnet/contracts/market/v0-4-market.clar:739) in a state where it mint shares whose backing was never received? Given that it chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:739` -> `calc-liquidation-params`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `calc-liquidation-params` returns is identical in both runs; a divergence confirms the finding.
