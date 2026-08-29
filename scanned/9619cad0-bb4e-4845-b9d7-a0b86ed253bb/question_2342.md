# Q2342: process-collateral-asset via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) have the same quantity scaled twice by two contracts that round differently? `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `collateral-receiver` varied, and assert that the value `process-collateral-asset` returns is identical in both runs; a divergence confirms the finding.
