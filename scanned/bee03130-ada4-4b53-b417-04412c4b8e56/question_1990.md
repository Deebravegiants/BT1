# Q1990: calc-liq-collateral-repay via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `calc-liq-collateral-repay` (mainnet/contracts/market/v0-4-market.clar:728) have the same quantity scaled twice by two contracts that round differently? `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:728` -> `calc-liq-collateral-repay`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the borrower targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
