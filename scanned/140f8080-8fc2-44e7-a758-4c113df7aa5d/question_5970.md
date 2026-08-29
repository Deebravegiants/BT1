# Q5970: filter-out-debt-asset via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) credit one side of an accounting pair without the other? `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `filter-out-debt-asset` never returns a value that breaks the invariant.
