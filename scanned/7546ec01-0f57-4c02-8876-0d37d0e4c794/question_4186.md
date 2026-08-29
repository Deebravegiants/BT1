# Q4186: user-safe-mask via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) destroy value through a truncation the opposite operation does not restore? `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `receiver`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
