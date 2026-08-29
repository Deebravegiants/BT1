# Q4750: write-feeds via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) destroy value through a truncation the opposite operation does not restore? `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `borrow` with `receiver`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
