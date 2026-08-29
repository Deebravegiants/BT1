# Q5906: calc-liq-collateral-repay via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `calc-liq-collateral-repay` (mainnet/contracts/market/v0-4-market.clar:728) credit one side of an accounting pair without the other? `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:728` -> `calc-liq-collateral-repay`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the borrower targeted varied, and assert that the value `calc-liq-collateral-repay` returns is identical in both runs; a divergence confirms the finding.
