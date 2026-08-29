# Q4778: subset via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the set of assets held, can an unprivileged attacker make `subset` (mainnet/contracts/market/v0-market-vault.clar:100) destroy value through a truncation the opposite operation does not restore? `subset` tests bitmask containment, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the set of assets held varied, and assert that the value `subset` returns is identical in both runs; a divergence confirms the finding.
