# Q4198: resolve-or-create via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) destroy value through a truncation the opposite operation does not restore? `resolve-or-create` allocates a user id through `increment` for whatever principal the market names, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with `receiver`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
