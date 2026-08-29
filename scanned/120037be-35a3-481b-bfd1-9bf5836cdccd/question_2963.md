# Q2963: filter-out-debt-asset via liquidate: count one deposit as backing for two simultaneous claims

## Question
`filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) rebuilds the debt list without one asset, under `as-max-len? ... u64`. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `debt-amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `debt-amount`, and assert the attacker's net token balance change is zero or negative.
