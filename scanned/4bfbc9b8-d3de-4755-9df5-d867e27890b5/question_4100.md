# Q4100: write-feed via liquidate-redeem: mint shares whose backing was never received

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) in a state where it mint shares whose backing was never received? Given that it applies one Pyth price-feed update and folds its status, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the borrower targeted varied, and assert that the value `write-feed` returns is identical in both runs; a divergence confirms the finding.
