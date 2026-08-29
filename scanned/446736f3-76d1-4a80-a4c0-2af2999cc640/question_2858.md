# Q2858: write-feed via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) have the same quantity scaled twice by two contracts that round differently? `write-feed` applies one Pyth price-feed update and folds its status, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with whether the position has any enabled debt row (the has-debt branch) varied, and assert that the value `write-feed` returns is identical in both runs; a divergence confirms the finding.
