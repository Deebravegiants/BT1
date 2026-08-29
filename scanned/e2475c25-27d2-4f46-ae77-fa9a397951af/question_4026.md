# Q4026: check-confidence via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) destroy value through a truncation the opposite operation does not restore? `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the position has any enabled debt row (the has-debt branch) across its boundary values through `collateral-remove` in simnet and assert `check-confidence` never returns a value that breaks the invariant.
