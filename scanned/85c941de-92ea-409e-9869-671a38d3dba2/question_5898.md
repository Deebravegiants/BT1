# Q5898: get-asset-value via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) credit one side of an accounting pair without the other? `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `get-asset-value` never returns a value that breaks the invariant.
