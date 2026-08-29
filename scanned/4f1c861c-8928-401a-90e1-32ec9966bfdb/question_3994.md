# Q3994: get-liquidation-position via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `receiver` for the underlying leg, can an unprivileged attacker make `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) destroy value through a truncation the opposite operation does not restore? `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `receiver` for the underlying leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
