# Q2546: process-collateral-asset via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) have the same quantity scaled twice by two contracts that round differently? `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `process-collateral-asset` returns is identical in both runs; a divergence confirms the finding.
