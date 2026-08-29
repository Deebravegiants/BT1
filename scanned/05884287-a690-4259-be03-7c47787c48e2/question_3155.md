# Q3155: calculate-asset-notional-value via liquidate: count one deposit as backing for two simultaneous claims

## Question
`calculate-asset-notional-value` (mainnet/contracts/market/v0-4-market.clar:544) normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `debt-amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:544` -> `calculate-asset-notional-value`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `calculate-asset-notional-value` normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `debt-amount`, and assert the attacker's net token balance change is zero or negative.
