# Q4282: normalize via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `normalize` (mainnet/contracts/market/v0-4-market.clar:576) destroy value through a truncation the opposite operation does not restore? `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:576` -> `normalize`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with `receiver`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
