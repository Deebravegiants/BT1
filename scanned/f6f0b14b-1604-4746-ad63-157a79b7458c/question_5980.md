# Q5980: create via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `create` (mainnet/contracts/market/v0-market-vault.clar:150) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it binds a principal to a fresh numeric id, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
