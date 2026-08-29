# Q0790: debt-remove-scaled via supply-collateral-add: mint shares whose backing was never received

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the position state the final collateral-add is validated against, can an unprivileged attacker make `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) mint shares whose backing was never received? `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with the position state the final collateral-add is validated against, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
