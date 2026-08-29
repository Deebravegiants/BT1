# Q5984: check-confidence via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `receiver`, including a contract principal reach `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `receiver`, including a contract principal varied, and assert that the value `check-confidence` returns is identical in both runs; a divergence confirms the finding.
