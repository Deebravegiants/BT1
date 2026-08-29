# Q4150: increment via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `increment` (mainnet/contracts/market/v0-market-vault.clar:137) destroy value through a truncation the opposite operation does not restore? `increment` advances the user-id nonce, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `increment` advances the user-id nonce. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `receiver`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
