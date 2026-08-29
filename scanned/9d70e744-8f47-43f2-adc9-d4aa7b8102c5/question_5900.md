# Q5900: filter-out-debt-asset via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it rebuilds the debt list without one asset, under `as-max-len? ... u64`, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `filter-out-debt-asset` returns is identical in both runs; a divergence confirms the finding.
