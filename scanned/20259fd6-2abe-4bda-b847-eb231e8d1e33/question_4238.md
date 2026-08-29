# Q4238: oracle-price-legal via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the set of assets held, can an unprivileged attacker make `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) destroy value through a truncation the opposite operation does not restore? `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the set of assets held varied, and assert that the value `oracle-price-legal` returns is identical in both runs; a divergence confirms the finding.
