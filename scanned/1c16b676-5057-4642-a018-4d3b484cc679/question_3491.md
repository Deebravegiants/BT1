# Q3491: calc-final-liquidation-amounts via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
`calc-final-liquidation-amounts` (mainnet/contracts/market/v0-4-market.clar:834) recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing how many entries share one price snapshot (price-feeds is passed as none), use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:834` -> `calc-final-liquidation-amounts`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with how many entries share one price snapshot (price-feeds is passed as none), and assert the attacker's net token balance change is zero or negative.
